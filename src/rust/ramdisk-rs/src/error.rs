use thiserror::Error;

pub type Result<T> = std::result::Result<T, Error>;

#[derive(Error, Debug)]
pub enum Error {
    #[error("invalid ramdisk size: {0} (must be > 0)")]
    SizeInvalid(u64),

    #[error("not enough free physical memory for a {requested} MiB ramdisk (only {available} MiB free)")]
    MemoryNotAvailable { requested: u64, available: u64 },

    #[error("this platform is not supported for ramdisk creation")]
    UnsupportedPlatform,

    #[error("required system tool not found: {0}")]
    ToolNotFound(String),

    #[error("must be root (or provide credentials) to create/manage this ramdisk")]
    PrivilegeRequired,

    #[error("command failed: {cmd}\nstdout: {stdout}\nstderr: {stderr}\nstatus: {status}")]
    CommandFailed {
        cmd: String,
        stdout: String,
        stderr: String,
        status: String,
    },

    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),

    #[error("path error: {0}")]
    Path(String),

    #[error("{0}")]
    Other(String),
}
