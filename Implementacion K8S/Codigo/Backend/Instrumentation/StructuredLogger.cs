using Microsoft.Extensions.Logging;
using InstrumentationInterface;

namespace Instrumentation
{
    public class StructuredLogger : IStructuredLogger
    {
        private readonly ILogger _logger;

        public StructuredLogger(ILogger<StructuredLogger> logger)
        {
            _logger = logger;
        }

        public void LogInformation(string message, Dictionary<string, object>? metadata = null)
        {
            var scopeData = BuildScopeData("Information", metadata);
            using (_logger.BeginScope(scopeData))
            {
                _logger.LogInformation(message);
            }
        }

        public void LogWarning(string message, Exception? exception = null, Dictionary<string, object>? metadata = null)
        {
            var scopeData = BuildScopeData("Warning", metadata);
            using (_logger.BeginScope(scopeData))
            {
                if (exception != null)
                {
                    _logger.LogWarning(exception, message);
                }
                else
                {
                    _logger.LogWarning(message);
                }
            }
        }

        public void LogError(string message, Exception? exception = null, Dictionary<string, object>? metadata = null)
        {
            var scopeData = BuildScopeData("Error", metadata);
            using (_logger.BeginScope(scopeData))
            {
                if (exception != null)
                {
                    _logger.LogError(exception, message);
                }
                else
                {
                    _logger.LogError(message);
                }
            }
        }

        private Dictionary<string, object> BuildScopeData(string logLevel, Dictionary<string, object>? metadata)
        {
            var scopeData = new Dictionary<string, object>
            {
                ["log_level"] = logLevel,
                ["timestamp"] = DateTime.UtcNow
            };

            if (metadata != null)
            {
                foreach (var kvp in metadata)
                {
                    scopeData[kvp.Key] = kvp.Value;
                }
            }

            return scopeData;
        }
    }
}

