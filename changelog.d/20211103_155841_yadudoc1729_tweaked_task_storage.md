### Added

- A new TaskStorage class that is designed to abstract the storage systems for result or payload blobs
- A RedisTaskStorage implementation and S3TaskStorage implementation which is ready for use for storing results.
- A ChainedTaskStorage class that wraps multiple storage implementations together to form more interesting storage options like
    : Store data into redis if size < 20KB else, store into S3.
