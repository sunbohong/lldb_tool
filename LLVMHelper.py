import lldb

def llvm_raw_ostream_enable(debugger, command, result, a, internal_dict):
    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand('br enable llvm_raw_ostream_enable' + command, returnObject)
    output = returnObject.GetOutput()
    groupList = re.match(r'\d*', output, re.M)
    if int(groupList.group(0)) > 0:
        print(output)
        return

    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(llvm::raw_ostream::Colors)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(char)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(llvm::StringRef)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(unsigned char)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(llvm::SmallVectorImpl<char> const&)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(unsigned long)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(long)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(unsigned long long)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(long long)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(llvm::format_object_base const&)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(void const*)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(double)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(llvm::formatv_object_base const&)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(llvm::FormattedString const&)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(llvm::FormattedNumber const&)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(llvm::FormattedBytes const&)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    interpreter.HandleCommand('br set -F "llvm::raw_ostream::operator<<(signed char)" -C "v " -N "llvm_raw_ostream_enable"' + command, returnObject)
    output = returnObject.GetOutput()
    print("18 breakpoints enabled.")

def llvm_raw_ostream_disable(debugger, command, result, a, internal_dict):
    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand('br disable llvm_raw_ostream_enable' + command, returnObject)
    output = returnObject.GetOutput()
    print(output)

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
        'command script add llvm_raw_ostream_enable -f LLVMHelper.llvm_raw_ostream_enable')
    debugger.HandleCommand(
        'command script add llvm_raw_ostream_disable -f LLVMHelper.llvm_raw_ostream_disable')
