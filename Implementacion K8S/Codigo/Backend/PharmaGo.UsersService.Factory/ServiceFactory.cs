using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Diagnostics;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using PharmaGo.UsersService.BusinessLogic;
using PharmaGo.DataAccess;
using PharmaGo.DataAccess.Repositories;
using PharmaGo.Domain.Entities;
using PharmaGo.UsersService.IBusinessLogic;
using PharmaGo.IDataAccess;
using Microsoft.Extensions.Hosting;
using InstrumentationInterface;
using Instrumentation;
using Polly;
using Polly.Extensions.Http;
using Microsoft.Extensions.Logging;


namespace PharmaGo.UsersService.Factory
{
    public static class ServiceFactory
    {

        public static void RegisterBusinessLogicServices(this IServiceCollection serviceCollection, IConfiguration configuration)
        {
            serviceCollection.AddScoped<ILoginManager, LoginManager>();
            serviceCollection.AddScoped<IUsersManager, UsersManager>();
            serviceCollection.AddScoped<IInvitationManager, InvitationManager>();
            serviceCollection.AddScoped<IRoleManager, RoleManager>();

            serviceCollection.AddHttpClient<PharmaGo.UsersService.HttpClients.PharmacyServiceClient>(client =>
            {
                var serviceUrl = configuration["ServiceUrls:PharmacyService"] ?? "http://127.0.0.1:5002";
                client.BaseAddress = new Uri(serviceUrl);
                client.Timeout = TimeSpan.FromSeconds(30);
            })
            .AddPolicyHandler(GetRetryPolicy())
            .AddPolicyHandler((services, request) => GetCircuitBreakerPolicy(services));
        }

        // 3 reintentos con backoff exponencial: 2s, 4s, 8s
        private static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy() =>
            HttpPolicyExtensions
                .HandleTransientHttpError()
                .WaitAndRetryAsync(
                    retryCount: 3,
                    sleepDurationProvider: attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt)));

        // Abre el circuito tras 5 fallas consecutivas, espera 30s antes de reintentar.
        // Loguea on Break/Reset/HalfOpen para que el evento quede visible en Kibana.
        //
        // IMPORTANTE: CircuitBreakerAsync es con estado (cuenta fallas consecutivas), asi que
        // la instancia de la policy debe crearse UNA SOLA VEZ y reutilizarse en todas las
        // requests. El overload AddPolicyHandler(Func<IServiceProvider,HttpRequestMessage,...>)
        // invoca este metodo en CADA request -- si se construyera la policy de nuevo cada vez,
        // cada llamada arrancaria con un circuito "recien nacido" y nunca llegaria a abrirse.
        // Por eso se cachea en un campo estatico con doble-check locking.
        private static IAsyncPolicy<HttpResponseMessage>? _pharmacyCircuitBreaker;
        private static readonly object _pharmacyCircuitBreakerLock = new();

        private static IAsyncPolicy<HttpResponseMessage> GetCircuitBreakerPolicy(IServiceProvider services)
        {
            if (_pharmacyCircuitBreaker != null) return _pharmacyCircuitBreaker;

            lock (_pharmacyCircuitBreakerLock)
            {
                if (_pharmacyCircuitBreaker != null) return _pharmacyCircuitBreaker;

                var logger = services.GetRequiredService<ILoggerFactory>()
                    .CreateLogger("PharmaGo.Resilience.CircuitBreaker.PharmacyServiceClient");

                _pharmacyCircuitBreaker = HttpPolicyExtensions
                    .HandleTransientHttpError()
                    .CircuitBreakerAsync(
                        handledEventsAllowedBeforeBreaking: 5,
                        durationOfBreak: TimeSpan.FromSeconds(30),
                        onBreak: (outcome, breakDelay) => logger.LogWarning(
                            "Circuit breaker OPEN for PharmacyServiceClient after 5 consecutive failures. Blocking calls for {BreakDelaySeconds}s. LastError={LastError}",
                            breakDelay.TotalSeconds, outcome.Exception?.Message ?? outcome.Result?.StatusCode.ToString()),
                        onReset: () => logger.LogInformation(
                            "Circuit breaker RESET (closed) for PharmacyServiceClient. PharmacyService is reachable again."),
                        onHalfOpen: () => logger.LogInformation(
                            "Circuit breaker HALF-OPEN for PharmacyServiceClient. Testing PharmacyService with next call."));

                return _pharmacyCircuitBreaker;
            }
        }

        public static void RegisterDataAccessServices(this IServiceCollection serviceCollection, IConfiguration configuration)
        {
            serviceCollection.AddScoped<IRepository<User>, UsersRepository>();
            serviceCollection.AddScoped<IRepository<Session>, SessionRepository>();
            serviceCollection.AddScoped<IRepository<Invitation>, InvitationRepository>();
            serviceCollection.AddScoped<IRepository<Role>, RoleRepository>();
            serviceCollection.AddScoped<IRepository<Pharmacy>, PharmacyRepository>();

            serviceCollection.AddDbContext<DbContext, PharmacyGoDbContext>(options =>
            {
                options.UseSqlServer(
                    configuration.GetConnectionString("DefaultConnection"),
                    sqlOptions => { sqlOptions.MigrationsAssembly("PharmaGo.DataAccess"); });
                options.ConfigureWarnings(w =>
                {
                    w.Ignore(RelationalEventId.CommandExecuted);
                    w.Ignore(RelationalEventId.CommandError);
                });
            });
            serviceCollection.AddSingleton<ICustomMetrics, CustomMetrics>();
            serviceCollection.AddSingleton<IStructuredLogger, StructuredLogger>();
        }

        public static IHost MigrateDatabase(this IHost host)
        {
            using (var scope = host.Services.CreateScope())
            {
                var dbContext = scope.ServiceProvider.GetRequiredService<DbContext>();
                dbContext.Database.Migrate();
            }

            return host;
        }

    }
}

