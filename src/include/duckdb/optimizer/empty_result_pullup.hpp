//===----------------------------------------------------------------------===//
//                         DuckDB
//
// duckdb/optimizer/empty_result_pullup.hpp
//
//
//===----------------------------------------------------------------------===//

#pragma once

#include "duckdb/optimizer/column_binding_replacer.hpp"

namespace duckdb {

//! The EmptyResultPullup Optimizer traverses the logical operator tree and Pulls up empty operators when possible
class EmptyResultPullup : LogicalOperatorVisitor {
public:
	EmptyResultPullup() {
	}

	unique_ptr<LogicalOperator> Optimize(unique_ptr<LogicalOperator> op);

private:
	unique_ptr<LogicalOperator> PullUpEmptyJoinChildren(unique_ptr<LogicalOperator> op);
};

} // namespace duckdb
