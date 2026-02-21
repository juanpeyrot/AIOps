using InstrumentationInterface;
using Microsoft.AspNetCore.Mvc;
using PharmaGo.UsersService.IBusinessLogic;
using PharmaGo.UsersService.Models.In;
using PharmaGo.UsersService.Models.Out;

namespace PharmaGo.UsersService.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class LoginController : ControllerBase
    {
        private readonly ILoginManager _loginManager;
        private readonly ICustomMetrics _customMetrics;
        private readonly IStructuredLogger _structuredLogger;

       public LoginController(ILoginManager manager, ICustomMetrics customMetrics, IStructuredLogger structuredLogger)
       {
            _loginManager = manager;
            _customMetrics = customMetrics;
            _structuredLogger = structuredLogger;
       }

        [HttpPost]
        public IActionResult Login([FromBody] LoginModelRequest userModel)
        {
            _customMetrics.LoginInvocations();
            
            try
            {
                var authorization = _loginManager.Login(userModel.UserName, userModel.Password);
                
                _structuredLogger.LogInformation(
                    $"User {authorization.UserName} logged in successfully",
                    new Dictionary<string, object>
                    {
                        ["status"] = "success",
                        ["message"] = $"User {authorization.UserName} logged in successfully",
                        ["user_name"] = authorization.UserName
                    }
                );
                
                return Ok(new LoginModelResponse() { token = authorization.Token, role = authorization.Role, userName = authorization.UserName });
            }
            catch (Exception ex)
            {
                _structuredLogger.LogWarning(
                    $"User {userModel.UserName} failed log in",
                    ex,
                    new Dictionary<string, object>
                    {
                        ["status"] = "failed",
                        ["message"] = $"User {userModel.UserName} failed log in",
                        ["user_name"] = userModel.UserName ?? "unknown"
                    }
                );
                
                throw;
            }
        }

    }
}

