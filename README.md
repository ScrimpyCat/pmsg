pmsg (Print Message)
====

LLDB and GDB scripts for pmsg command. The command displays the current Objective-C message about to be called.


The command should be executed either when at a message send (objc_msgSend or variant) or whenever all the correct aspects are still initialized correctly (at the beginning of the method).

To load the script in GDB: `(gdb) source pmsg_gdb`
To load the script in LLDB: `(lldb) command script import pmsg_lldb.py`

Example usage and output: 

	0x00007fff97970f40 in -[NSCGSContext(NSQuartzCoreAdditions) CIContext] ()
	1: x/i $pc  0x7fff97970f40 <-[NSCGSContext(NSQuartzCoreAdditions) CIContext]+536>:    callq  0x7fff97ec94d2 <dyld_stub_objc_msgSend>
	(gdb) pmsg
	[CIContext contextWithCGContext:0x102128420 options:(null)]

	0x00007fff97970fb6 in -[NSCGSContext(NSQuartzCoreAdditions) CIContext] ()
	1: x/i $pc  0x7fff97970fb6 <-[NSCGSContext(NSQuartzCoreAdditions) CIContext]+654>:    callq  0x7fff97ec94d2 <dyld_stub_objc_msgSend>
	(gdb) pmsg
	[NSMapTable mapTableWithWeakToStrongObjects]

	0x00007fff97971024 in -[NSCGSContext(NSQuartzCoreAdditions) CIContext] ()
	1: x/i $pc  0x7fff97971024 <-[NSCGSContext(NSQuartzCoreAdditions) CIContext]+764>:    callq  0x7fff97ec94d2 <dyld_stub_objc_msgSend>
	(gdb) pmsg
	[NSMapTable {
	}
	setObject:<CIContext: 0x10030ebb0> forKey:<NSWindowGraphicsContext: 0x1021274b0>]

	1: x/i $pc  0x100f89 <main+89>:    callq  *%r9
	(gdb) pmsg
	[NSString stringWithContentsOfFile:@"/blah/blah/blah.txt" usedEncoding:0x7fff5fbffba8 error:0x0]

	1: x/i $pc  0x10000103b <main+267>:    callq  *%r8
	(gdb) pmsg
	[NSMutableArray arrayWithCapacity:10]


- - -

It currently only supports x86_64 architecture, may be updated to support others in the future (well the LLDB version). 


Both scripts are incomplete at the moment. The LLDB script will be updated over time to support the missing features, while the old GDB script will not.

Currently missing features:
 * GDB/LLDB: No support for structures or unions
 * GDB/LLDB: Does not allow for arguments on the stack
 * GDB/LLDB: Won't be able to process arguments marked with certain qualifiers (const, byref, etc.)
 * GDB/LLDB: Won't display the arguments in a varadic function
 * GDB/LLDB: Doesn't support all message send variants.
 * GDB/LLDB: Other architectures besides x86_64

As a disclaimer I don't know Python so the LLDB is pretty messy/hacked together and could be made much better. So improvements are certainly welcome. If LLDB ever gets around to supporting Ruby I'll port it to that and do a proper implementation.