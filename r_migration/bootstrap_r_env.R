# Bootstrap R dependencies for the migration scripts.

required_packages <- c("httr2", "jsonlite")

install_missing <- function(pkgs = required_packages) {
  missing <- pkgs[!(pkgs %in% rownames(installed.packages()))]
  if (length(missing) == 0) {
    cat("All required R packages are already installed.\n")
    return(invisible(TRUE))
  }

  cat("Installing:", paste(missing, collapse = ", "), "\n")
  install.packages(missing, repos = "https://cloud.r-project.org")
  invisible(TRUE)
}

if (sys.nframe() == 0) {
  install_missing()
}
