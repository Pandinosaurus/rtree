
import atexit, os, re, sys
import ctypes
from ctypes.util import find_library

import ctypes

class RTreeError(Exception):
    "RTree exception, indicates a RTree-related error."
    pass

def check_return(result, func, cargs):
    "Error checking for Error calls"
    if result != 0:
        msg = 'LASError in "%s": %s' % (func.__name__, rt.Error_GetLastErrorMsg() )
        rt.Error_Reset()
        raise RTreeError(msg)
    return True

def check_void(result, func, cargs):
    "Error checking for void* returns"
    if not bool(result):
        msg = 'Error in "%s": %s' % (func.__name__, rt.Error_GetLastErrorMsg() )
        rt.Error_Reset()
        raise RTreeError(msg)
    return result

def check_void_done(result, func, cargs):
    "Error checking for void* returns that might be empty with no error"
    if rt.Error_GetErrorCount():
        msg = 'Error in "%s": %s' % (func.__name__, rt.Error_GetLastErrorMsg() )
        rt.Error_Reset()
        raise RTreeError(msg)
        
    return result

def check_value(result, func, cargs):
    "Error checking proper value returns"
    count = rt.Error_GetErrorCount()
    if count != 0:
        msg = 'Error in "%s": %s' % (func.__name__, rt.Error_GetLastErrorMsg() )
        rt.Error_Reset()
        raise RTreeError(msg)
    return result

def check_value_free(result, func, cargs):
    "Error checking proper value returns"
    count = rt.Error_GetErrorCount()
    if count != 0:
        msg = 'Error in "%s": %s' % (func.__name__, rt.Error_GetLastErrorMsg() )
        rt.Error_Reset()
        raise RTreeError(msg)
    retval = ctypes.string_at(result)[:]
    free(result)
    return retval

def free_returned_char_p(result, func, cargs):

    size = ctypes.c_int()
    retvalue = ctypes.string_at(result)
    free(result)
    return retvalue
    
    

try:
    from numpy import array, ndarray
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

if os.name == 'nt':
    lib_name = 'spatialindex1_c.dll'
    try:
        local_dlls = os.path.abspath(os.__file__ + "../../../DLLs")
        original_path = os.environ['PATH']
        os.environ['PATH'] = "%s;%s" % (local_dlls, original_path)
        rt = ctypes.PyDLL(lib_name)
        def free(m):
            try:
                free = ctypes.cdll.msvcrt.free(m)
            except WindowsError:
                pass
    except (ImportError, WindowsError):
        raise
elif os.name == 'posix':
    platform = os.uname()[0]
    lib_name = 'libspatialindex_c.so'
    if platform == 'Darwin':
        lib_name = 'libspatialindex_c.dylib'
        free = ctypes.CDLL(find_library('libc')).free
    else:
        free = ctypes.CDLL(find_library('libc.so.6')).free
    rt = ctypes.CDLL(lib_name)
else:
    raise RTreeError('Unsupported OS "%s"' % os.name)

rt.Error_GetLastErrorNum.restype = ctypes.c_int

rt.Error_GetLastErrorMsg.restype = ctypes.POINTER(ctypes.c_char)
rt.Error_GetLastErrorMsg.errcheck = free_returned_char_p

rt.Error_GetLastErrorMethod.restype = ctypes.POINTER(ctypes.c_char)
rt.Error_GetLastErrorMethod.errcheck = free_returned_char_p

rt.Error_GetErrorCount.restype=ctypes.c_int

rt.Index_Create.argtypes = [ctypes.c_void_p]
rt.Index_Create.restype = ctypes.c_void_p
rt.Index_Create.errcheck = check_void

NEXTFUNC = ctypes.CFUNCTYPE(ctypes.c_int, 
                            ctypes.POINTER(ctypes.c_uint64),
                            ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),
                            ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),
                            ctypes.POINTER(ctypes.c_uint32),
                            ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)),
                            ctypes.POINTER(ctypes.c_uint32))

rt.Index_CreateWithStream.argtypes = [ctypes.c_void_p, NEXTFUNC] 
rt.Index_CreateWithStream.restype = ctypes.c_void_p
rt.Index_CreateWithStream.errcheck = check_void

rt.Index_Destroy.argtypes = [ctypes.c_void_p]
rt.Index_Destroy.restype = None
rt.Index_Destroy.errcheck = check_void_done

rt.Index_GetProperties.argtypes = [ctypes.c_void_p]
rt.Index_GetProperties.restype = ctypes.c_void_p
rt.Index_GetProperties.errcheck = check_void

rt.Index_DeleteData.argtypes = [ctypes.c_void_p, 
                                ctypes.c_uint64, 
                                ctypes.POINTER(ctypes.c_double), 
                                ctypes.POINTER(ctypes.c_double), 
                                ctypes.c_uint32]
rt.Index_DeleteData.restype = ctypes.c_int
rt.Index_DeleteData.errcheck = check_return

rt.Index_InsertData.argtypes = [ctypes.c_void_p, 
                                ctypes.c_uint64, 
                                ctypes.POINTER(ctypes.c_double), 
                                ctypes.POINTER(ctypes.c_double), 
                                ctypes.c_uint32, 
                                ctypes.POINTER(ctypes.c_ubyte), 
                                ctypes.c_uint32]
rt.Index_InsertData.restype = ctypes.c_int
rt.Index_InsertData.errcheck = check_return

rt.Index_GetBounds.argtypes = [ ctypes.c_void_p,
                                ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),
                                ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),
                                ctypes.POINTER(ctypes.c_uint32)]
rt.Index_GetBounds.restype = ctypes.c_int
rt.Index_GetBounds.errcheck = check_value

rt.Index_IsValid.argtypes = [ctypes.c_void_p]
rt.Index_IsValid.restype = ctypes.c_int
rt.Index_IsValid.errcheck = check_value

rt.Index_Intersects_obj.argtypes = [ctypes.c_void_p,
                                    ctypes.POINTER(ctypes.c_double), 
                                    ctypes.POINTER(ctypes.c_double), 
                                    ctypes.c_uint32, 
                                    ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)),
                                    ctypes.POINTER(ctypes.c_uint32)]
rt.Index_Intersects_obj.restype = ctypes.c_int
rt.Index_Intersects_obj.errcheck = check_return

rt.Index_Intersects_id.argtypes = [ctypes.c_void_p,
                                    ctypes.POINTER(ctypes.c_double), 
                                    ctypes.POINTER(ctypes.c_double), 
                                    ctypes.c_uint32, 
                                    ctypes.POINTER(ctypes.POINTER(ctypes.c_uint64)),
                                    ctypes.POINTER(ctypes.c_uint32)]
rt.Index_Intersects_id.restype = ctypes.c_int
rt.Index_Intersects_id.errcheck = check_return

rt.Index_NearestNeighbors_obj.argtypes = [  ctypes.c_void_p,
                                            ctypes.POINTER(ctypes.c_double), 
                                            ctypes.POINTER(ctypes.c_double), 
                                            ctypes.c_uint32, 
                                            ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)),
                                            ctypes.POINTER(ctypes.c_uint32)]
rt.Index_NearestNeighbors_obj.restype = ctypes.c_int
rt.Index_NearestNeighbors_obj.errcheck = check_return

rt.Index_NearestNeighbors_id.argtypes = [  ctypes.c_void_p,
                                            ctypes.POINTER(ctypes.c_double), 
                                            ctypes.POINTER(ctypes.c_double), 
                                            ctypes.c_uint32, 
                                            ctypes.POINTER(ctypes.POINTER(ctypes.c_uint64)),
                                            ctypes.POINTER(ctypes.c_uint32)]
rt.Index_NearestNeighbors_id.restype = ctypes.c_int
rt.Index_NearestNeighbors_id.errcheck = check_return

rt.Index_GetLeaves.argtypes = [ ctypes.c_void_p,
                                ctypes.POINTER(ctypes.c_uint32), 
                                ctypes.POINTER(ctypes.POINTER(ctypes.c_uint32)), 
                                ctypes.POINTER(ctypes.POINTER(ctypes.c_int64)), 
                                ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(ctypes.c_int64))),
                                ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(ctypes.c_double))),
                                ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(ctypes.c_double))),
                                ctypes.POINTER(ctypes.c_uint32)]
rt.Index_GetLeaves.restype = ctypes.c_int
rt.Index_GetLeaves.errcheck = check_return

rt.Index_DestroyObjResults.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)), ctypes.c_uint32]
rt.Index_DestroyObjResults.restype = None
rt.Index_DestroyObjResults.errcheck = check_void_done

rt.Index_Free.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
rt.Index_Free.restype = None
rt.Index_Free.errcheck = check_void_done

rt.IndexItem_Destroy.argtypes = [ctypes.c_void_p]
rt.IndexItem_Destroy.restype = None
rt.IndexItem_Destroy.errcheck = check_void_done

rt.IndexItem_GetData.argtypes = [   ctypes.c_void_p, 
                                    ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)), 
                                    ctypes.POINTER(ctypes.c_uint64)]
rt.IndexItem_GetData.restype = ctypes.c_int
rt.IndexItem_GetData.errcheck = check_value

rt.IndexItem_GetBounds.argtypes = [ ctypes.c_void_p,
                                    ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),
                                    ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),
                                    ctypes.POINTER(ctypes.c_uint32)]
rt.IndexItem_GetBounds.restype = ctypes.c_int
rt.IndexItem_GetBounds.errcheck = check_value

rt.IndexItem_GetID.argtypes = [ctypes.c_void_p]
rt.IndexItem_GetID.restype = ctypes.c_uint64
rt.IndexItem_GetID.errcheck = check_value

rt.IndexProperty_Create.restype = ctypes.c_void_p
rt.IndexProperty_Create.errcheck = check_void

rt.IndexProperty_Destroy.argtypes = [ctypes.c_void_p]
rt.IndexProperty_Destroy.restype = None
rt.IndexProperty_Destroy.errcheck = check_void_done

rt.IndexProperty_SetIndexType.argtypes = [ctypes.c_void_p, ctypes.c_int32]
rt.IndexProperty_SetIndexType.restype = ctypes.c_int
rt.IndexProperty_SetIndexType.errcheck = check_return

rt.IndexProperty_GetIndexType.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetIndexType.restype = ctypes.c_int
rt.IndexProperty_GetIndexType.errcheck = check_value

rt.IndexProperty_SetDimension.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetDimension.restype = ctypes.c_int
rt.IndexProperty_SetDimension.errcheck = check_return

rt.IndexProperty_GetDimension.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetDimension.restype = ctypes.c_int
rt.IndexProperty_GetDimension.errcheck = check_value

rt.IndexProperty_SetIndexVariant.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetIndexVariant.restype = ctypes.c_int
rt.IndexProperty_SetIndexVariant.errcheck = check_return

rt.IndexProperty_GetIndexVariant.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetIndexVariant.restype = ctypes.c_int
rt.IndexProperty_GetIndexVariant.errcheck = check_value

rt.IndexProperty_SetIndexStorage.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetIndexStorage.restype = ctypes.c_int
rt.IndexProperty_SetIndexStorage.errcheck = check_return

rt.IndexProperty_GetIndexStorage.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetIndexStorage.restype = ctypes.c_int
rt.IndexProperty_GetIndexStorage.errcheck = check_value

rt.IndexProperty_SetIndexCapacity.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetIndexCapacity.restype = ctypes.c_int
rt.IndexProperty_SetIndexCapacity.errcheck = check_return

rt.IndexProperty_GetIndexCapacity.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetIndexCapacity.restype = ctypes.c_int
rt.IndexProperty_GetIndexCapacity.errcheck = check_value

rt.IndexProperty_SetLeafCapacity.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetLeafCapacity.restype = ctypes.c_int
rt.IndexProperty_SetLeafCapacity.errcheck = check_return

rt.IndexProperty_GetLeafCapacity.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetLeafCapacity.restype = ctypes.c_int
rt.IndexProperty_GetLeafCapacity.errcheck = check_value

rt.IndexProperty_SetPagesize.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetPagesize.restype = ctypes.c_int
rt.IndexProperty_SetPagesize.errcheck = check_return

rt.IndexProperty_GetPagesize.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetPagesize.restype = ctypes.c_int
rt.IndexProperty_GetPagesize.errcheck = check_value

rt.IndexProperty_SetLeafPoolCapacity.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetLeafPoolCapacity.restype = ctypes.c_int
rt.IndexProperty_SetLeafPoolCapacity.errcheck = check_return

rt.IndexProperty_GetLeafPoolCapacity.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetLeafPoolCapacity.restype = ctypes.c_int
rt.IndexProperty_GetLeafPoolCapacity.errcheck = check_value

rt.IndexProperty_SetIndexPoolCapacity.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetIndexPoolCapacity.restype = ctypes.c_int
rt.IndexProperty_SetIndexPoolCapacity.errcheck = check_return

rt.IndexProperty_GetIndexPoolCapacity.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetIndexPoolCapacity.restype = ctypes.c_int
rt.IndexProperty_GetIndexPoolCapacity.errcheck = check_value

rt.IndexProperty_SetRegionPoolCapacity.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetRegionPoolCapacity.restype = ctypes.c_int
rt.IndexProperty_SetRegionPoolCapacity.errcheck = check_return

rt.IndexProperty_GetRegionPoolCapacity.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetRegionPoolCapacity.restype = ctypes.c_int
rt.IndexProperty_GetRegionPoolCapacity.errcheck = check_value

rt.IndexProperty_SetPointPoolCapacity.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetPointPoolCapacity.restype = ctypes.c_int
rt.IndexProperty_SetPointPoolCapacity.errcheck = check_return

rt.IndexProperty_GetPointPoolCapacity.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetPointPoolCapacity.restype = ctypes.c_int
rt.IndexProperty_GetPointPoolCapacity.errcheck = check_value

rt.IndexProperty_SetBufferingCapacity.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetBufferingCapacity.restype = ctypes.c_int
rt.IndexProperty_SetBufferingCapacity.errcheck = check_return

rt.IndexProperty_GetBufferingCapacity.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetBufferingCapacity.restype = ctypes.c_int
rt.IndexProperty_GetBufferingCapacity.errcheck = check_value

rt.IndexProperty_SetEnsureTightMBRs.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetEnsureTightMBRs.restype = ctypes.c_int
rt.IndexProperty_SetEnsureTightMBRs.errcheck = check_return

rt.IndexProperty_GetEnsureTightMBRs.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetEnsureTightMBRs.restype = ctypes.c_int
rt.IndexProperty_GetEnsureTightMBRs.errcheck = check_value

rt.IndexProperty_SetOverwrite.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetOverwrite.restype = ctypes.c_int
rt.IndexProperty_SetOverwrite.errcheck = check_return

rt.IndexProperty_GetOverwrite.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetOverwrite.restype = ctypes.c_int
rt.IndexProperty_GetOverwrite.errcheck = check_value

rt.IndexProperty_SetNearMinimumOverlapFactor.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetNearMinimumOverlapFactor.restype = ctypes.c_int
rt.IndexProperty_SetNearMinimumOverlapFactor.errcheck = check_return

rt.IndexProperty_GetNearMinimumOverlapFactor.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetNearMinimumOverlapFactor.restype = ctypes.c_int
rt.IndexProperty_GetNearMinimumOverlapFactor.errcheck = check_value

rt.IndexProperty_SetWriteThrough.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rt.IndexProperty_SetWriteThrough.restype = ctypes.c_int
rt.IndexProperty_SetWriteThrough.errcheck = check_return

rt.IndexProperty_GetWriteThrough.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetWriteThrough.restype = ctypes.c_int
rt.IndexProperty_GetWriteThrough.errcheck = check_value

rt.IndexProperty_SetFillFactor.argtypes = [ctypes.c_void_p, ctypes.c_double]
rt.IndexProperty_SetFillFactor.restype = ctypes.c_int
rt.IndexProperty_SetFillFactor.errcheck = check_return

rt.IndexProperty_GetFillFactor.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetFillFactor.restype = ctypes.c_double
rt.IndexProperty_GetFillFactor.errcheck = check_value

rt.IndexProperty_SetSplitDistributionFactor.argtypes = [ctypes.c_void_p, ctypes.c_double]
rt.IndexProperty_SetSplitDistributionFactor.restype = ctypes.c_int
rt.IndexProperty_SetSplitDistributionFactor.errcheck = check_return

rt.IndexProperty_GetSplitDistributionFactor.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetSplitDistributionFactor.restype = ctypes.c_double
rt.IndexProperty_GetSplitDistributionFactor.errcheck = check_value

rt.IndexProperty_SetTPRHorizon.argtypes = [ctypes.c_void_p, ctypes.c_double]
rt.IndexProperty_SetTPRHorizon.restype = ctypes.c_int
rt.IndexProperty_SetTPRHorizon.errcheck = check_return

rt.IndexProperty_GetTPRHorizon.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetTPRHorizon.restype = ctypes.c_double
rt.IndexProperty_GetTPRHorizon.errcheck = check_value

rt.IndexProperty_SetReinsertFactor.argtypes = [ctypes.c_void_p, ctypes.c_double]
rt.IndexProperty_SetReinsertFactor.restype = ctypes.c_int
rt.IndexProperty_SetReinsertFactor.errcheck = check_return

rt.IndexProperty_GetReinsertFactor.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetReinsertFactor.restype = ctypes.c_double
rt.IndexProperty_GetReinsertFactor.errcheck = check_value

rt.IndexProperty_SetFileName.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
rt.IndexProperty_SetFileName.restype = ctypes.c_int
rt.IndexProperty_SetFileName.errcheck = check_return

rt.IndexProperty_GetFileName.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetFileName.errcheck = check_value_free

rt.IndexProperty_SetFileNameExtensionDat.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
rt.IndexProperty_SetFileNameExtensionDat.restype = ctypes.c_int
rt.IndexProperty_SetFileNameExtensionDat.errcheck = check_return

rt.IndexProperty_GetFileNameExtensionDat.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetFileNameExtensionDat.errcheck = check_value_free

rt.IndexProperty_SetFileNameExtensionIdx.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
rt.IndexProperty_SetFileNameExtensionIdx.restype = ctypes.c_int
rt.IndexProperty_SetFileNameExtensionIdx.errcheck = check_return

rt.IndexProperty_GetFileNameExtensionIdx.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetFileNameExtensionIdx.errcheck = check_value_free

rt.IndexProperty_SetIndexID.argtypes = [ctypes.c_void_p, ctypes.c_int64]
rt.IndexProperty_SetIndexID.restype = ctypes.c_int
rt.IndexProperty_SetIndexID.errcheck = check_return

rt.IndexProperty_GetIndexID.argtypes = [ctypes.c_void_p]
rt.IndexProperty_GetIndexID.restype = ctypes.c_int64
rt.IndexProperty_GetIndexID.errcheck = check_value

rt.SIDX_Version.restype = ctypes.POINTER(ctypes.c_char)
rt.SIDX_Version.errcheck = free_returned_char_p
