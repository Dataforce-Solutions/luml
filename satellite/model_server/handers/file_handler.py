import httpx


class FileHandler:
    @staticmethod
    def _calculate_optimal_chunk_size(file_size: int) -> int:
        if file_size < 10485760:  # 10mb
            return 1048576  # 1mb
        if file_size < 52428800:  # 50mb
            return 4194304  # 4mb
        if file_size < 104857600:  # 100mb
            return 16777216  # 16mb
        if file_size < 524288000:  # 500mb
            return 67108864  # 64mb
        if file_size < 1073741824:  # 1gb
            return 134217728  # 128mb
        if file_size < 5368709120:  # 5gb
            return 268435456  # 256mb
        return 268435456  # 256mb

    def download_file(self, url: str, file_path: str) -> str:
        try:
            timeout = httpx.Timeout(connect=30.0, read=300.0, write=60.0, pool=30.0)

            with httpx.stream("GET", url, timeout=timeout) as response:
                response.raise_for_status()

                total_size = int(response.headers.get("content-length", 0))

                chunk_size = self._calculate_optimal_chunk_size(total_size)

                with open(file_path, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=chunk_size):
                        f.write(chunk)

            return file_path
        except Exception as error:
            raise ValueError(f" Error: {error}") from error
