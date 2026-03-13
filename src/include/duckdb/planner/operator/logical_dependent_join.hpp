//===----------------------------------------------------------------------===//
//                         DuckDB
//
// duckdb/planner/operator/logical_dependent_join.hpp
//
//
//===----------------------------------------------------------------------===//

#pragma once

#include "duckdb/planner/binder.hpp"
#include "duckdb/planner/operator/logical_comparison_join.hpp"
#include "duckdb/planner/expression/bound_subquery_expression.hpp"

namespace duckdb {

class LogicalDependentJoin : public LogicalComparisonJoin {
public:
	static constexpr const LogicalOperatorType TYPE = LogicalOperatorType::LOGICAL_DEPENDENT_JOIN;

public:
	explicit LogicalDependentJoin(unique_ptr<LogicalOperator> left, unique_ptr<LogicalOperator> right,
	                              CorrelatedColumns correlated_columns, JoinType type,
	                              unique_ptr<Expression> condition);

	explicit LogicalDependentJoin(JoinType type);

	//! The conditions of the join
	unique_ptr<Expression> join_condition;
	//! The list of columns that have correlations with the right
	CorrelatedColumns correlated_columns;

	SubqueryType subquery_type = SubqueryType::INVALID;
	bool perform_delim = true;
	bool any_join = false;
	bool propagate_null_values = true;
	bool is_lateral_join = false;

	vector<unique_ptr<Expression>> arbitrary_expressions;
	vector<unique_ptr<Expression>> expression_children;
	vector<LogicalType> child_types;
	vector<LogicalType> child_targets;
	ExpressionType comparison_type;

public:
	static unique_ptr<LogicalOperator> Create(unique_ptr<LogicalOperator> left, unique_ptr<LogicalOperator> right,
	                                          CorrelatedColumns correlated_columns, JoinType type,
	                                          unique_ptr<Expression> condition);
};
} // namespace duckdb
