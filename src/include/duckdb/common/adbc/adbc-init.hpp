//===----------------------------------------------------------------------===//
//                         DuckDB
//
// duckdb/common/adbc/adbc-init.hpp
//
//
//===----------------------------------------------------------------------===//

#pragma once

#ifndef DUCKDB_ADBC_INIT
#define DUCKDB_ADBC_INIT

#include "duckdb.h"
#include "duckdb/common/adbc/adbc.hpp"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint8_t AdbcStatusCode;

//! We gotta leak the symbols of the init function
DUCKDB_C_API AdbcStatusCode duckdb_adbc_init(int version, void *driver, struct AdbcError *error);

#ifdef __cplusplus
}
#endif

#endif
