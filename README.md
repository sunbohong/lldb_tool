# lldb_tool
This is a collection of LLDB commands to assist debugging.


# 前言

本仓库用于维护作者使用的一些小众 lldb 脚本。

## 使用说明

创建文件 `~/.lldbinit`，并添加以下代码

```
command script import /path/to/lldb.py
```
## 命令列表
|  文件  | 命令 | 参数说明 | 使用说明 |
|----|------|------|---|
|   pvtable.py |   vt |   c++ 实例地址  |   `vt this` `vt a` `vt ptrA`， 打印实例的虚函数列表    | 
|   LLVMHelper.py   |   llvm_raw_ostream_enable  |   无   |   启动 `llvm::raw_ostream::operator<<` 部分断点（断点名称是`llvm_raw_ostream_enable`）， 会自动在触发打点时，打印当前环境变量   |
|   LLVMHelper.py    |   llvm_raw_ostream_disable |   无   |   停用所有名称是`llvm_raw_ostream_enable` 的断点

## 背景

lldb 提供了~~非常好用~~ 的 Python 接口，通过这些基础接口，我们可以实现一些提高开发和调试的功能。Facebook 出品的 chisel 工具库就是其中的佼佼者。

考虑到 chisel 面向用户众多，一些小众的需求需要寻求其它解决方案。

## pvtable.py

lldb 目前缺失打印虚函数表的功能。本仓库提供了 `vt this` 命令，用于打印实例的虚函数表。


```
(lldb) vt a
0x100002048: 0x00000001000011d0 ++`A::TEST_B() at main.cpp:17

0x100002050: 0x00000001000011e0 ++`A::TEST_C() at main.cpp:26

0x100002058: 0x00000001000011f0 ++`A::TEST_A() at main.cpp:27

(lldb) vt ptrB
0x100002080: 0x00000001000011d0 ++`A::TEST_B() at main.cpp:17

0x100002088: 0x00000001000011e0 ++`A::TEST_C() at main.cpp:26

0x100002090: 0x0000000100001260 ++`B::TEST_A() at main.cpp:32

0x100002098: 0x0000000100001270 ++`B::TEST_E() at main.cpp:31

(lldb) 
```

说明：第一列代表**实例所指向的虚函数的某一项**，第二列代表**函数在内存中的地址**，第三列代表**代码函数所在 module的位置** + **函数所在源码位置**


## llvm_output_enable.py

笔者在调试 llvm 源码时，经常面临在 `llvm::raw_ostream::operator<<`位置添加断点需求。

通常情况下，我们会通过 `b llvm::raw_ostream::operator<<` 命令添加断点的方式解决该诉求。

但是在解决问题的同时，该方案也带来了一些新问题。

如下所示，当参数是 `(char *)` 类型时，它会依次命中 2 个断点：`raw_ostream &operator<<(const char *Str)` 和 `raw_ostream &operator<<(StringRef Str)`，这会带来非常多不便。

```
OS << << "note: "
```

```c++
  raw_ostream &operator<<(const char *Str) {
    // Inline fast path, particularly for constant strings where a sufficiently
    // smart compiler will simplify strlen.

    return this->operator<<(StringRef(Str));
  }


  raw_ostream &operator<<(StringRef Str) {
    // Inline fast path, particularly for strings with a known length.
    size_t Size = Str.size();

    // Make sure we can use the fast path.
    if (Size > (size_t)(OutBufEnd - OutBufCur))
      return write(Str.data(), Size);

    if (Size) {
      memcpy(OutBufCur, Str.data(), Size);
      OutBufCur += Size;
    }
    return *this;
  }
```


实际上，上述命令会在下面 **21** 个函数入口设置断点（其中3个属于可以忽略的常用函数）。

```
152: name = 'llvm::raw_ostream::operator<<', locations = 21, resolved = 21, hit count = 0
  152.1: where = dsymutil`llvm::raw_ostream::operator<<(char const*) at raw_ostream.h:196, address = 0x0000000100002a80, resolved, hit count = 0 
  152.2: where = dsymutil`llvm::raw_ostream::operator<<(llvm::StringRef) at raw_ostream.h:181, address = 0x0000000100002ac0, resolved, hit count = 0 
  152.3: where = dsymutil`llvm::raw_ostream::operator<<(char) at raw_ostream.h:160, address = 0x000000010002d460, resolved, hit count = 0 
  152.4: where = dsymutil`llvm::raw_ostream::operator<<(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&) at raw_ostream.h:203, address = 0x000000010002e650, resolved, hit count = 0 
  152.5: where = dsymutil`llvm::raw_ostream::operator<<(llvm::SmallVectorImpl<char> const&) at raw_ostream.h:208, address = 0x000000010002fde0, resolved, hit count = 0 
  152.6: where = dsymutil`llvm::raw_ostream::operator<<(unsigned int) at raw_ostream.h:218, address = 0x0000000100564aa0, resolved, hit count = 0 
  152.7: where = dsymutil`llvm::raw_ostream::operator<<(int) at raw_ostream.h:222, address = 0x0000000100dc4b50, resolved, hit count = 0 
  152.8: where = dsymutil`llvm::raw_ostream::operator<<(unsigned long) at raw_ostream.cpp:122, address = 0x000000010209c4c0, resolved, hit count = 0 
  152.9: where = dsymutil`llvm::raw_ostream::operator<<(long) at raw_ostream.cpp:127, address = 0x000000010209c500, resolved, hit count = 0 
  152.10: where = dsymutil`llvm::raw_ostream::operator<<(unsigned long long) at raw_ostream.cpp:132, address = 0x000000010209c540, resolved, hit count = 0 
  152.11: where = dsymutil`llvm::raw_ostream::operator<<(long long) at raw_ostream.cpp:137, address = 0x000000010209c580, resolved, hit count = 0 
  152.12: where = dsymutil`llvm::raw_ostream::operator<<(llvm::raw_ostream::Colors) at raw_ostream.cpp:147, address = 0x000000010209c650, resolved, hit count = 0 
  152.13: where = dsymutil`llvm::raw_ostream::operator<<(llvm::format_object_base const&) at raw_ostream.cpp:305, address = 0x000000010209c780, resolved, hit count = 0 
  152.14: where = dsymutil`llvm::raw_ostream::operator<<(unsigned char) at raw_ostream.h:167, address = 0x000000010209cc50, resolved, hit count = 0 
  152.15: where = dsymutil`llvm::raw_ostream::operator<<(void const*) at raw_ostream.cpp:205, address = 0x000000010209ccc0, resolved, hit count = 0 
  152.16: where = dsymutil`llvm::raw_ostream::operator<<(double) at raw_ostream.cpp:210, address = 0x000000010209cd20, resolved, hit count = 0 
  152.17: where = dsymutil`llvm::raw_ostream::operator<<(llvm::formatv_object_base const&) at raw_ostream.cpp:345, address = 0x000000010209d370, resolved, hit count = 0 
  152.18: where = dsymutil`llvm::raw_ostream::operator<<(llvm::FormattedString const&) at raw_ostream.cpp:351, address = 0x000000010209d590, resolved, hit count = 0 
  152.19: where = dsymutil`llvm::raw_ostream::operator<<(llvm::FormattedNumber const&) at raw_ostream.cpp:379, address = 0x000000010209d7e0, resolved, hit count = 0 
  152.20: where = dsymutil`llvm::raw_ostream::operator<<(llvm::FormattedBytes const&) at raw_ostream.cpp:402, address = 0x000000010209da20, resolved, hit count = 0 
  152.21: where = dsymutil`llvm::raw_ostream::operator<<(signed char) at raw_ostream.h:174, address = 0x0000000102fcaa80, resolved, hit count = 0 
```


针对以上情况，本仓库提供了一份专用的命令 `llvm_raw_ostream_enable`，该命令会只在必要的函数位置设置断点。
如下所示。

```
153: name = 'llvm::raw_ostream::operator<<(llvm::raw_ostream::Colors)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  153.1: where = dsymutil`llvm::raw_ostream::operator<<(llvm::raw_ostream::Colors) at raw_ostream.cpp:147, address = 0x000000010209c650, resolved, hit count = 0 

154: name = 'llvm::raw_ostream::operator<<(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  154.1: where = dsymutil`llvm::raw_ostream::operator<<(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&) at raw_ostream.h:203, address = 0x000000010002e650, resolved, hit count = 0 

155: name = 'llvm::raw_ostream::operator<<(char)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  155.1: where = dsymutil`llvm::raw_ostream::operator<<(char) at raw_ostream.h:160, address = 0x000000010002d460, resolved, hit count = 0 

156: name = 'llvm::raw_ostream::operator<<(llvm::StringRef)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  156.1: where = dsymutil`llvm::raw_ostream::operator<<(llvm::StringRef) at raw_ostream.h:181, address = 0x0000000100002ac0, resolved, hit count = 0 

157: name = 'llvm::raw_ostream::operator<<(unsigned char)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  157.1: where = dsymutil`llvm::raw_ostream::operator<<(unsigned char) at raw_ostream.h:167, address = 0x000000010209cc50, resolved, hit count = 0 

158: name = 'llvm::raw_ostream::operator<<(llvm::SmallVectorImpl<char> const&)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  158.1: where = dsymutil`llvm::raw_ostream::operator<<(llvm::SmallVectorImpl<char> const&) at raw_ostream.h:208, address = 0x000000010002fde0, resolved, hit count = 0 

159: name = 'llvm::raw_ostream::operator<<(unsigned long)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  159.1: where = dsymutil`llvm::raw_ostream::operator<<(unsigned long) at raw_ostream.cpp:122, address = 0x000000010209c4c0, resolved, hit count = 0 

160: name = 'llvm::raw_ostream::operator<<(long)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  160.1: where = dsymutil`llvm::raw_ostream::operator<<(long) at raw_ostream.cpp:127, address = 0x000000010209c500, resolved, hit count = 0 

161: name = 'llvm::raw_ostream::operator<<(unsigned long long)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  161.1: where = dsymutil`llvm::raw_ostream::operator<<(unsigned long long) at raw_ostream.cpp:132, address = 0x000000010209c540, resolved, hit count = 0 

162: name = 'llvm::raw_ostream::operator<<(long long)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  162.1: where = dsymutil`llvm::raw_ostream::operator<<(long long) at raw_ostream.cpp:137, address = 0x000000010209c580, resolved, hit count = 0 

163: name = 'llvm::raw_ostream::operator<<(llvm::format_object_base const&)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  163.1: where = dsymutil`llvm::raw_ostream::operator<<(llvm::format_object_base const&) at raw_ostream.cpp:305, address = 0x000000010209c780, resolved, hit count = 0 

164: name = 'llvm::raw_ostream::operator<<(void const*)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  164.1: where = dsymutil`llvm::raw_ostream::operator<<(void const*) at raw_ostream.cpp:205, address = 0x000000010209ccc0, resolved, hit count = 0 

165: name = 'llvm::raw_ostream::operator<<(double)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  165.1: where = dsymutil`llvm::raw_ostream::operator<<(double) at raw_ostream.cpp:210, address = 0x000000010209cd20, resolved, hit count = 0 

166: name = 'llvm::raw_ostream::operator<<(llvm::formatv_object_base const&)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  166.1: where = dsymutil`llvm::raw_ostream::operator<<(llvm::formatv_object_base const&) at raw_ostream.cpp:345, address = 0x000000010209d370, resolved, hit count = 0 

167: name = 'llvm::raw_ostream::operator<<(llvm::FormattedString const&)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  167.1: where = dsymutil`llvm::raw_ostream::operator<<(llvm::FormattedString const&) at raw_ostream.cpp:351, address = 0x000000010209d590, resolved, hit count = 0 

168: name = 'llvm::raw_ostream::operator<<(llvm::FormattedNumber const&)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  168.1: where = dsymutil`llvm::raw_ostream::operator<<(llvm::FormattedNumber const&) at raw_ostream.cpp:379, address = 0x000000010209d7e0, resolved, hit count = 0 

169: name = 'llvm::raw_ostream::operator<<(llvm::FormattedBytes const&)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  169.1: where = dsymutil`llvm::raw_ostream::operator<<(llvm::FormattedBytes const&) at raw_ostream.cpp:402, address = 0x000000010209da20, resolved, hit count = 0 

170: name = 'llvm::raw_ostream::operator<<(signed char)', locations = 1, resolved = 1, hit count = 0
    Breakpoint commands:
      v 

  Names:
    llvm_raw_ostream_enable

  170.1: where = dsymutil`llvm::raw_ostream::operator<<(signed char) at raw_ostream.h:174, address = 0x0000000102fcaa80, resolved, hit count = 0 
```
