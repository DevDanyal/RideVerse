using System.Threading;
using System.Threading.Tasks;
using RideVerse.Core;

namespace RideVerse.API
{
    public interface IPlayerApi
    {
        Task<ApiResult<Auth.PlayerProfile>> GetMyProfileAsync(CancellationToken ct = default);
        Task<ApiResult<Auth.PlayerProfile>> UpdateProfileAsync(string displayName, CancellationToken ct = default);
        Task<ApiResult<Auth.PlayerStatisticsResponse>> GetStatisticsAsync(CancellationToken ct = default);
    }

    public class PlayerApi : IPlayerApi
    {
        private readonly ApiClient _client;

        public PlayerApi(ApiClient client)
        {
            _client = client;
        }

        public async Task<ApiResult<Auth.PlayerProfile>> GetMyProfileAsync(CancellationToken ct = default)
        {
            return await _client.GetAsync<Auth.PlayerProfile>(Constants.Api.Players.Me, ct);
        }

        public async Task<ApiResult<Auth.PlayerProfile>> UpdateProfileAsync(
            string displayName, CancellationToken ct = default)
        {
            var update = new { display_name = displayName };
            return await _client.PatchAsync<Auth.PlayerProfile>(Constants.Api.Players.Me, update, ct);
        }

        public async Task<ApiResult<Auth.PlayerStatisticsResponse>> GetStatisticsAsync(
            CancellationToken ct = default)
        {
            return await _client.GetAsync<Auth.PlayerStatisticsResponse>(
                Constants.Api.Players.MeStatistics, ct);
        }
    }
}
