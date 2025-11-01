"""
清理环境变量后启动程序
"""

import os
import sys

print("=" * 80)
print("🔧 清理 Tkinter 环境变量")
print("=" * 80)

# 清除错误的环境变量
if 'TCL_LIBRARY' in os.environ:
    old_tcl = os.environ['TCL_LIBRARY']
    print(f"\n❌ 发现错误的 TCL_LIBRARY: {old_tcl}")
    del os.environ['TCL_LIBRARY']
    print("✅ 已清除")

if 'TK_LIBRARY' in os.environ:
    old_tk = os.environ['TK_LIBRARY']
    print(f"\n❌ 发现错误的 TK_LIBRARY: {old_tk}")
    del os.environ['TK_LIBRARY']
    print("✅ 已清除")

# 设置正确的环境变量（Python 安装目录下的 tcl）
python_dir = os.path.dirname(sys.executable)
tcl_dir = os.path.join(python_dir, 'tcl')

if os.path.exists(tcl_dir):
    # 寻找 tcl8.6 和 tk8.6 目录
    tcl86_dir = os.path.join(tcl_dir, 'tcl8.6')
    tk86_dir = os.path.join(tcl_dir, 'tk8.6')
    
    if os.path.exists(tcl86_dir):
        os.environ['TCL_LIBRARY'] = tcl86_dir
        print(f"\n✅ 设置 TCL_LIBRARY: {tcl86_dir}")
    
    if os.path.exists(tk86_dir):
        os.environ['TK_LIBRARY'] = tk86_dir
        print(f"✅ 设置 TK_LIBRARY: {tk86_dir}")

print("\n" + "=" * 80)
print("🚀 启动程序")
print("=" * 80 + "\n")

# 导入并运行主程序
import main
main.main()


