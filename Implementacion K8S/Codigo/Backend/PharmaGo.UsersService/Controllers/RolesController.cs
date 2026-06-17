using Microsoft.AspNetCore.Mvc;
using Polly.CircuitBreaker;
using PharmaGo.UsersService.HttpClients;
using PharmaGo.UsersService.IBusinessLogic;
using PharmaGo.UsersService.Models.Out;

namespace PharmaGo.UsersService.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class RolesController : ControllerBase
    {
        private readonly IRoleManager _roleManager;
        private readonly PharmacyServiceClient _pharmacyServiceClient;

        public RolesController(IRoleManager manager, PharmacyServiceClient pharmacyServiceClient)
        {
            _roleManager = manager;
            _pharmacyServiceClient = pharmacyServiceClient;
        }

        [HttpGet]
        public IActionResult GetAll()
        {
            var roles = _roleManager.GetAll();
            IEnumerable<RoleModelResponse> result = roles.Select(role => new RoleModelResponse(role));
            return Ok(result);
        }

        [HttpGet("test")]
        public IActionResult Test()
        {
            // Endpoint simple de prueba que siempre devuelve 200
            return Ok(new { status = "ok", message = "Service is healthy" });
        }

        [HttpGet("ping")]
        public IActionResult Ping()
        {
            // Endpoint simple de prueba que siempre devuelve 200 - sin dependencias
            return Ok(new { status = "ok", message = "pong", timestamp = DateTime.UtcNow });
        }

        [HttpGet("pharmacy-status")]
        public async Task<IActionResult> PharmacyStatus()
        {
            // Llama a PharmacyService a traves del cliente con Circuit Breaker (Polly).
            // Sirve para demostrar el patron con trafico real: si PharmacyService cae,
            // el circuito abre tras 5 fallas consecutivas y este endpoint responde 503
            // de inmediato (sin esperar el timeout) hasta que el circuito vuelve a cerrar.
            try
            {
                var isUp = await _pharmacyServiceClient.PingAsync();
                return isUp
                    ? Ok(new { status = "ok", pharmacyService = "up" })
                    : StatusCode(503, new { status = "error", pharmacyService = "down" });
            }
            catch (BrokenCircuitException)
            {
                return StatusCode(503, new { status = "error", pharmacyService = "circuit_open" });
            }
            catch (Exception)
            {
                return StatusCode(503, new { status = "error", pharmacyService = "unreachable" });
            }
        }

    }
}

