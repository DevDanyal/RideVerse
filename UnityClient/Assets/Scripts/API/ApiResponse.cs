namespace RideVerse.API
{
    public enum ApiRequestStatus
    {
        Success,
        Unauthorized,
        Forbidden,
        NotFound,
        ValidationError,
        ServerError,
        NetworkError,
        Cancelled
    }

    public class ApiResult<T>
    {
        public ApiRequestStatus Status;
        public T Data;
        public string Message;
        public string ErrorCode;

        public bool IsSuccess => Status == ApiRequestStatus.Success;

        public static ApiResult<T> Success(T data, string message = "OK")
        {
            return new ApiResult<T> { Status = ApiRequestStatus.Success, Data = data, Message = message };
        }

        public static ApiResult<T> Fail(ApiRequestStatus status, string message, string errorCode = null)
        {
            return new ApiResult<T> { Status = status, Message = message, ErrorCode = errorCode };
        }
    }
}
