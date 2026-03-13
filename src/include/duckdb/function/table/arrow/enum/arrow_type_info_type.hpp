//===----------------------------------------------------------------------===//
//                         DuckDB
//
// duckdb/function/table/arrow/enum/arrow_type_info_type.hpp
//
//
//===----------------------------------------------------------------------===//

#pragma once

#include <cstdint>

namespace duckdb {

enum class ArrowTypeInfoType : uint8_t { LIST, STRUCT, DATE_TIME, STRING, ARRAY, DECIMAL };

} // namespace duckdb
