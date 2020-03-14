# encoding=utf-8
import sys
sys.path.append('/Applications/Xcode-beta.app/Contents/SharedFrameworks/LLDB.framework/Resources/Python/lldb')
import lldb
import re

PointerByteSize = 8

def pvtable(debugger, command, result, internal_dict):
    # print(type(debugger))
    # print(type(command))
    # print(type(result))
    # print(type(internal_dict))
    # print(debugger.GetSelectedTarget())
    # print(debugger.GetSelectedTarget().GetProcess())
    
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()

    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand('x/a &' + command, returnObject)
    # print('x/a ' + command)
    output = returnObject.GetOutput()

    #  0x7ffeefbfe350: 0x0000000103dce2b0 dsymutil`vtable for llvm::yaml::Output + 16
    # print("output-1: %s" % output)
   
    # &this 会报错，需要特殊处理
    
    # error: invalid start address expression.
    # error: address expression "&this" evaluation failed
    if output == None:
        interpreter.HandleCommand('x/a ' + command, returnObject)
        output = returnObject.GetOutput()
        # print("output-2: %s" % output)


    if output:
        groupList = re.match(r'(.*) (.*vtable) for (.*) \+ (.*)', output, re.M)

        # print(groupList)

        # print(groupList.group(0))

        # # 0x7ffeefbfe350: 0x0000000103dce2b0 
        # print(groupList.group(1))

        # # dsymutil`vtable
        # print(groupList.group(2))

        # # llvm::yaml::Output
        # print(groupList.group(3))

        # # 16
        # print(groupList.group(4))

    else:
        print('Oops!!!');
        return;


    # first vtable 
    objAddressStr = groupList.group(1).split().pop()
    # print("objAddressStr: %s" % objAddressStr)

    objAddress = int(objAddressStr, 16)

    # print("objAddress: %s" % objAddress)

    #  p (void *)*((unsigned long *)*(unsigned long *)test + 0)
    #  p (void *)*((unsigned long *)*(unsigned long *)&test + 0)
    error = lldb.SBError()

    typename = groupList.group(3)
    # print("typename: %s" % typename)

    vtblSymbol = 'vtable for ' + typename
    # print("\"" + vtblSymbol + "\"")

    # image lookup -r -v -s "vtable for llvm::raw_svector_ostream"
    symbols = target.FindSymbols(vtblSymbol)
    for sc in symbols:
        # print("sc: %s" % sc)
        startP = sc.symbol.GetStartAddress().GetLoadAddress(target)
        endP = sc.symbol.GetEndAddress().GetLoadAddress(target)
        # skip 16 byte
        startP = startP + 16;        
        while startP < endP:
            interpreter.HandleCommand('x/a ' + str(objAddress), returnObject)
            output = returnObject.GetOutput()
            print(output)
            objAddress = objAddress + PointerByteSize;
            startP = startP + PointerByteSize;


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
        'command script add vt -f pvtable.pvtable')
 
