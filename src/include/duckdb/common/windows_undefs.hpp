//===----------------------------------------------------------------------===//
//                         DuckDB
//
// duckdb/common/windows_undefs.hpp
//
//
//===----------------------------------------------------------------------===//

#ifdef WIN32

#ifdef min
#undef min
#endif

#ifdef max
#undef max
#endif

#ifdef ERROR
#undef ERROR
#endif

#ifdef small
#undef small
#endif

#ifdef CreateDirectory
#undef CreateDirectory
#endif

#ifdef MoveFile
#undef MoveFile
#endif

#ifdef RemoveDirectory
#undef RemoveDirectory
#endif

#ifdef UUID
#undef UUID
#endif

#ifdef interface
#undef interface
#endif

#ifdef DELETE
#undef DELETE
#endif

#endif
