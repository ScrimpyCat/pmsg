#command script import pmsg_lldb.py
import lldb
import commands
import optparse
import shlex

def getDescription(frame, expr):
    desc = frame.EvaluateExpression('(char*)[[' + str(expr) + ' description] UTF8String]').GetSummary()
    if desc is None: return '(null)'
    return desc.strip('"')


def stripTypeQualifiers(str):
    return str.lstrip('rnNoORV')


def pmsg(debugger, command, result, internal_dict):
    frame = debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame()
    
    regs = frame.GetRegisters()['General Purpose Registers'][0]
    fregs = frame.GetRegisters()['Floating Point Registers'][0]
    obj = getDescription(frame, '$rdi')
    msg = '[' + obj

    methodsig = frame.EvaluateExpression('(id)[' + ('$rdi' if regs.GetChildMemberWithName('rdi').GetValueAsUnsigned() != 0 else '[NSObject class]') + ' methodSignatureForSelector: $rsi]')
    selector = frame.EvaluateExpression('(id)[NSStringFromSelector($rsi) componentsSeparatedByString: @":"]')
    argcount = frame.EvaluateExpression('(uint64_t)[' + str(methodsig.GetValueAsUnsigned()) + ' numberOfArguments]').GetValueAsUnsigned()
    
    if argcount == 2:
        msg += ' ' + getDescription(frame, '[' + str(selector.GetValueAsUnsigned()) + ' objectAtIndex: 0]')
    else:
        ints = 2
        floats = 0
        for i in range(2,argcount):
            msg += ' ' + getDescription(frame, '[' + str(selector.GetValueAsUnsigned()) + ' objectAtIndex: ' + str(i-2) + ']') + ':'
            argtype = stripTypeQualifiers(frame.EvaluateExpression('(char*)[' + str(methodsig.GetValueAsUnsigned()) + ' getArgumentTypeAtIndex: ' + str(i) + ']').GetSummary().strip('"'))
            
            if ints == 2:
                currentObjecti = regs.GetChildMemberWithName('rdx')
            elif ints == 3:
                currentObjecti = regs.GetChildMemberWithName('rcx')
            elif ints == 4:
                currentObjecti = regs.GetChildMemberWithName('r8')
            elif ints == 5:
                currentObjecti = regs.GetChildMemberWithName('r9')
            else:
                currentObjecti = None

            if floats == 0:
                currentObjectf = fregs.GetChildMemberWithName('xmm0')
            elif floats == 1:
                currentObjectf = fregs.GetChildMemberWithName('xmm1')
            elif floats == 2:
                currentObjectf = fregs.GetChildMemberWithName('xmm2')
            elif floats == 3:
                currentObjectf = fregs.GetChildMemberWithName('xmm3')
            elif floats == 4:
                currentObjectf = fregs.GetChildMemberWithName('xmm4')
            elif floats == 5:
                currentObjectf = fregs.GetChildMemberWithName('xmm5')
            elif floats == 6:
                currentObjectf = fregs.GetChildMemberWithName('xmm6')
            elif floats == 7:
                currentObjectf = fregs.GetChildMemberWithName('xmm7')
            else:
                currentObjectf = None

            if currentObjectf == None or currentObjecti == None: continue

            if argtype[0] == '@':
                ints += 1
                obj = str(currentObjecti.GetValueAsUnsigned())
                desc = getDescription(frame, obj)

                if frame.EvaluateExpression('(int)[' + obj + ' isKindOfClass: [NSString class]]').GetValueAsUnsigned() == 1:
                    msg += '@"' + desc + '"'
                else:
                    msg += desc
            elif argtype[0] == '^':
                ints += 1
                msg += hex(currentObjecti.GetValueAsUnsigned())
            elif argtype[0] == '*':
                ints += 1
                s = frame.EvaluateExpression('(char*)' + str(currentObjecti.GetValueAsUnsigned())).GetSummary()
                msg += s if s is not None else '(null)'
            elif argtype[0] == 'i':
                ints += 1
                msg += str(currentObjecti.GetValueAsSigned())
            elif argtype[0] == 'c':
                ints += 1
                msg += str(currentObjecti.GetValueAsSigned())
            elif argtype[0] == 's':
                ints += 1
                msg += str(currentObjecti.GetValueAsSigned())
            elif argtype[0] == 'l':
                ints += 1
                msg += str(currentObjecti.GetValueAsSigned())
            elif argtype[0] == 'q':
                ints += 1
                msg += str(currentObjecti.GetValueAsSigned())
            elif argtype[0] == 'C':
                ints += 1
                msg += str(currentObjecti.GetValueAsUnsigned())
            elif argtype[0] == 'I':
                ints += 1
                msg += str(currentObjecti.GetValueAsUnsigned())
            elif argtype[0] == 'S':
                ints += 1
                msg += str(currentObjecti.GetValueAsUnsigned())
            elif argtype[0] == 'L':
                ints += 1
                msg += str(currentObjecti.GetValueAsUnsigned())
            elif argtype[0] == 'Q':
                ints += 1
                msg += str(currentObjecti.GetValueAsUnsigned())
            elif argtype[0] == 'B':
                ints += 1
                msg += 'false' if currentObjecti.GetValueAsUnsigned() == 0 else 'true'
            elif argtype[0] == '#':
                ints += 1
                cls = str(currentObjecti.GetValueAsUnsigned())
                msg += getDescription(frame, cls)
            elif argtype[0] == ':':
                ints += 1
                s = frame.EvaluateExpression('(char*)sel_getName(' + str(currentObjecti.GetValueAsUnsigned()) + ')').GetSummary()
                msg += ('@selector(' + s.strip('"') + ')') if s is not None else '(null)'
            elif argtype[0] == 'f':
                floats += 1
                msg += getDescription(frame, '[NSNumber numberWithFloat: ((float __attribute__((ext_vector_type(4))))$xmm0)[0]]')
            elif argtype[0] == 'd':
                floats += 1
                msg += getDescription(frame, '[NSNumber numberWithDouble: ((double __attribute__((ext_vector_type(2))))$xmm0)[0]]')
            else:
                #Just assume it would be an integer
                ints += 1
                print '(' + str(i-2) + ') Unsupported type:', argtype


    print >>result, msg + ']'


# And the initialization code to add your commands 
def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f pmsg_lldb.pmsg pmsg')
    print 'The "pmsg" python command has been installed and is ready for use.'