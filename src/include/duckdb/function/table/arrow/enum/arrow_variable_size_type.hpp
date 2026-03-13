//===----------------------------------------------------------------------===//
//                         DuckDB
//
// duckdb/function/table/arrow/enum/arrow_variable_size_type.hpp
//
//
//===----------------------------------------------------------------------===//

#pragma once

namespace duckdb {

//===--------------------------------------------------------------------===//
// Arrow Variable Size Types
//===--------------------------------------------------------------------===//
enum class ArrowVariableSizeType : uint8_t { NORMAL, FIXED_SIZE, SUPER_SIZE, VIEW };

} // namespace duckdb
