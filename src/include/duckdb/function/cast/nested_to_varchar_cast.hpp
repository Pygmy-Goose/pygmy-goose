//===----------------------------------------------------------------------===//
//                         DuckDB
//
// duckdb/function/cast/nested_to_varchar_cast.hpp
//
//
//===----------------------------------------------------------------------===//

#pragma once

namespace duckdb {

struct NestedToVarcharCast {
public:
	static const bool LOOKUP_TABLE[256];
};

} // namespace duckdb
