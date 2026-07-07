##############################################
# Interpreter for Aram Programming Language
##############################################

import AramParser, AramBuiltIns, AramImport, error
from sys import exit

# Function to return tamil words for True & False
def TFEngtoTamil(truthValue):
    if truthValue:
        return u'உண்மை'
    else:
        return u'பொய்'

# Function to return english words for உண்மை & பொய்
def TFTamiltoEng(tamilword):
    if tamilword == u'உண்மை':
        return True
    elif tamilword == u'பொய்':
        return False

############################################################
# Interpreter class to perform interpretation and execution
############################################################

class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.hasErrored = False
        
        self.SYMBOL_TABLE = {} # Global symbol table
        self.LOCAL_SCOPE_SYMBOL_TABLE = {}  # Lobal Symbol table (used when inside a function)
        
        # All the built-in functions of Aram
        # 'func_name' : [no.of.formalparams, Call to function]
        self.BUILT_IN_FUNCTIONS = {'வெளியேறு': [0, AramBuiltIns.வெளியேறு],
                                'வகை': [1, AramBuiltIns.வகை],
                                'முழுஎண்': [1, AramBuiltIns.முழுஎண்],
                                'புள்ளிஎண்': [1, AramBuiltIns.புள்ளிஎண்],
                                'வாக்கியம்': [1, AramBuiltIns.வாக்கியம்],
                                'round': [1, AramBuiltIns.round],
                                'power': [2, AramBuiltIns.power],
                               
                                'get_pi': [0, AramBuiltIns.get_pi],
                                'get_e': [0, AramBuiltIns.get_e],
                                'get_tau': [0, AramBuiltIns.get_tau],
                                'ceil': [1, AramBuiltIns.ceil],
                                'floor': [1, AramBuiltIns.floor],
                                'sin': [1, AramBuiltIns.sin],
                                'cos': [1, AramBuiltIns.cos],
                                'tan': [1, AramBuiltIns.tan],
                                'factorial': [1, AramBuiltIns.factorial],
                                'mod': [2, AramBuiltIns.mod],
                                'gcd': [2, AramBuiltIns.gcd],
                                'lcm': [2, AramBuiltIns.lcm],
                                'sqrt': [1, AramBuiltIns.sqrt],
                                'radians': [1, AramBuiltIns.radians],
                                'degrees': [1, AramBuiltIns.degrees],
                                'randint': [2, AramBuiltIns.randint],
                                'choice': [1, AramBuiltIns.choice],
                                'random': [0, AramBuiltIns.random],
                                'திற': [1, AramBuiltIns.திற],   ####FILE
                                'நிறுத்து': [2, AramBuiltIns.நிறுத்து],
                                'படி': [1, AramBuiltIns.படி],
                                'எழுது': [2, AramBuiltIns.எழுது],
                                'மூடு': [1, AramBuiltIns.மூடு],
                                'துவக்கம்': [1, AramBuiltIns.துவக்கம்],
                                'சேர்க்க': [2,AramBuiltIns.சேர்க்க],
                                'பிரி': [3, AramBuiltIns.பிரி],
                                'இணை': [2, AramBuiltIns.இணை],
                                'தொடர்': [2, AramBuiltIns.தொடர்],
                                'நீளம்': [1, AramBuiltIns.நீளம்],
                                'நீக்கு':[2, self.நீக்கு],
                                'உறுப்பு_சேர்': [2, self.உறுப்பு_சேர்],
                                'இடைச்செருகு': [3, self.இடைச்செருகு],
                                'உள்ளது':[2,AramBuiltIns.உள்ளது],
                                'பட்டியல்_உருவாக்கு': [1, AramBuiltIns.பட்டியல்_உருவாக்கு],
                                'தொகுப்பு_உருவாக்கு': [1, AramBuiltIns.தொகுப்பு_உருவாக்கு],
                                'கணம்_உருவாக்கு': [1, AramBuiltIns.கணம்_உருவாக்கு]
                                }
        self.DECLARED_FUNCTIONS = {} # Dictionary to hold function definitions defined by the user
        self.insideLoop = False
        self.breakLoop = False
        self.continueLoop = False
        self.insideFunction = False
    
    # method to perform interpretation
    def interpret(self):
             
        return self.statements(self.ast), self.hasErrored

    # method to handle binary operation
    def binaryOperator(self, bin_op_node):
        left = bin_op_node.leftOp
        right = bin_op_node.rightOp

        if left == None or right == None:
            error.Error("Binary operationல் பிழை")
            self.hasErrored = True
             

        leftVal = self.visitNode(left)
        rightVal = self.visitNode(right)
        
        if bin_op_node.op in ('BIT_AND', 'BIT_OR', 'BIT_XOR', 'LSHIFT', 'RSHIFT'):
            if type(leftVal) != int or type(rightVal) != int:
                error.Error("பிழை: முழுஎண்களில் மட்டுமே Bitwise operations செய்ய முடியும்")
                self.hasErrored = True
                 
            if bin_op_node.op == 'BIT_AND':
                return leftVal & rightVal
            elif bin_op_node.op == 'BIT_OR':
                return leftVal | rightVal
            elif bin_op_node.op == 'BIT_XOR':
                return leftVal ^ rightVal
            elif bin_op_node.op == 'LSHIFT':
                return leftVal << rightVal
            elif bin_op_node.op == 'RSHIFT':
                return leftVal >> rightVal

        if type(rightVal) == str and type(leftVal) == str:
            if bin_op_node.op == 'PLUS':
                return leftVal + rightVal
            error.Error("பிழை: வாக்கியத்துடன் பொருந்தா Binary operation")
            self.hasErrored = True
             
        elif type(rightVal) == str or type(leftVal) == str:
            error.Error("பிழை: வாக்கியத்துடன் பொருந்தா Binary operation")
            self.hasErrored = True
             
        if type(rightVal) == list and type(leftVal) == list:
            if bin_op_node.op == 'PLUS':
                return leftVal + rightVal
            error.Error("பிழை: பட்டியலுடன் பொருந்தா Binary operation")
            self.hasErrored = True
             
        elif type(rightVal) == list or type(leftVal) == list:
            error.Error("பிழை: பட்டியலுடன் பொருந்தா Binary operation")
            self.hasErrored = True
             
        else:
            # Appropriate result for specific operator
            if bin_op_node.op == 'PLUS':
                return leftVal + rightVal
            elif bin_op_node.op == 'MINUS':
                return leftVal - rightVal
            elif bin_op_node.op == 'MUL':
                return leftVal * rightVal
            elif bin_op_node.op == 'DIV':
                if rightVal == 0 or rightVal == 0.0:
                    error.Error("கணித பிழை: வகுக்கும் எண் '0' ஆக இருக்க முடியாது!")
                    raise RuntimeError("கணித பிழை: வகுக்கும் எண் '0' ஆக இருக்க முடியாது!")
                return leftVal / rightVal
            elif bin_op_node.op == 'MOD':
                return leftVal % rightVal
    
    # method to handle number value
    def numberValue(self, num_node):
        type = num_node.type
        if type == 'INT':
            return int(num_node.value)
        elif type == 'FLOAT':
            return float(num_node.value)
    
    # method to handle string value
    def stringValue(self, str_node):
        return str_node.value
    
    # method to handle unary operation
    def unaryValue(self, unary_node):
        val = self.visitNode(unary_node.exp)
        if unary_node.op == 'PLUS':
            return +val
        elif unary_node.op == 'MINUS':
            return -val
        elif unary_node.op == 'BIT_NOT':
            if type(val) != int:
                error.Error("பிழை: முழுஎண்களில் மட்டுமே Bitwise NOT செய்ய முடியும்", str(val))
                self.hasErrored = True
                 
            return ~val
        elif unary_node.op == 'NOT':
            if type(val) != int and type(val)!= float:
                val = TFTamiltoEng(val)
            val = not val
            return TFEngtoTamil(val)
    
    # method to create list datatype
    def listNode(self, list_node):
        temp = list(map(self.visitNode, list_node.elements))
        return temp
    
    # method to handle list indexing
    def listIndexValue(self, list_index_node):
        listelements = self.visitNode(list_index_node.listelement)
        if type(listelements) != list:
            error.Error("பட்டியலில் மட்டுமே indexing செய்ய முடியும்  ")
            self.hasErrored = True
             
        index = self.visitNode(list_index_node.index)
        if type(index) != int:
            error.Error("'பட்டியல்[ ]' உள் ஒரு முழுஎண்(0 அல்லது அதற்கு மேல்) எதிர்பார்க்கப்பட்டது")
            self.hasErrored = True
             
        if index < 0:
            error.Error("'பட்டியல்[ ]' உள் ஒரு முழுஎண்(0 அல்லது அதற்கு மேல்) எதிர்பார்க்கப்பட்டது")
            self.hasErrored = True
             
        try:
            return listelements[index]
        except:
            error.Error("பட்டியல்[ ] index range வெளியே சென்றது", listelements)
            self.hasErrored = True
             
    
    # method to handle assignment statement
    def assignStatement(self, assign_node):
        varName = assign_node.left.value
        if self.insideFunction:
            self.LOCAL_SCOPE_SYMBOL_TABLE[varName] = self.visitNode(assign_node.right)
        else:
            self.SYMBOL_TABLE[varName] = self.visitNode(assign_node.right)
    
    # method to get the value of a variable
    def variableValue(self, var_node):
        varName = var_node.value
        #val = self.SYMBOL_TABLE.get(varName)
        val = self.LOCAL_SCOPE_SYMBOL_TABLE.get(varName)
        if val == None:
            val = self.SYMBOL_TABLE.get(varName)
            if val == None:
                error.Error('அறிவிக்கப்படாத பெயர் பயன்பாடு', varName)
                self.hasErrored = True
                 
            else:
                return val
        else:
            return val
    
    # method to execute each statement
    def statements(self, statements_node):
        for statement in statements_node.children:
            self.visitNode(statement)
    
    # method to execute print()
    def _format_for_print(self, val, hex_preview=64):
        # 1) Bytes / Bytearray
        if isinstance(val, (bytes, bytearray)):
            try:
                # Try to decode as UTF-8 (Tamil-friendly)
                return val.decode("utf-8",errors="ignore")
            except UnicodeDecodeError:
                # Fallback: clean hex preview for true binary
                hex_part = " ".join(f"{b:02X}" for b in val[:hex_preview])
                if len(val) > hex_preview:
                    hex_part += " ..."
                return f"[பைனரி {len(val)} bytes] {hex_part}"

        # 2) List: format elements recursively
        if isinstance(val, list):
            return "[" + ", ".join(self._format_for_print(x) for x in val) + "]"

        # 3) Everything else
        return str(val)

    # --- Replace your printValue with this version ---
    def printValue(self, print_node):
        argument = print_node.expr
        for i in argument:
            val = self.visitNode(i)
            out = self._format_for_print(val)

            # Only unescape \n and \t for decoded text, not for binary hex tags
            # (Safe heuristic: if it starts with [பைனரி ...], leave as-is)
            if not out.startswith("[பைனரி"):
                out = out.replace('\\n', '\n').replace('\\t', '\t')

            end = ' ' if i is not argument[-1] else '\n'
            print(out, end=end)


    # method to evaluate input()
    def inputValue(self, inp_node):
        display = self.visitNode(inp_node.expr)
        display = str(display)
        display = display.replace('\\n', '\n')
        display = display.replace('\\t', '\t')
        print(display, end='')
        inp = input()
        try:
            inp = eval(inp)
        except:
            pass
            #print('Detected string input')
        return inp
    
    # method to handle comparison operation
    def comparisonOperator(self, comp_node):
        left = self.visitNode(comp_node.leftOp)
        right = self.visitNode(comp_node.rightOp)
        operator = comp_node.op
        #'EQ', 'NOT_EQ', 'LESS_EQ', 'LESS', 'GREATER_EQ', 'GREATER'
        if operator == 'EQ':
            val = (left == right)
        elif operator == 'NOT_EQ':
            val = (left != right)
        elif operator == 'LESS_EQ':
            val = (left <= right)
        elif operator == 'LESS':
            val = (left < right)
        elif operator == 'GREATER_EQ':
            val = (left >= right)
        elif operator == 'GREATER':
            val = (left > right)
        return TFEngtoTamil(val)
    
    # method to handle logical operation
    def logicalOperator(self, logical_node):
        left = self.visitNode(logical_node.leftOp)
        right = self.visitNode(logical_node.rightOp)
        if left == 1.0:
            left = 1
        if right == 1.0:
            right = 1
        if left == 0.0:
            left = 0
        if right == 0.0:
            right = 0
        if type(left) == int and type(right) == int:
            pass
        elif type(left) == int and (type(right) != int and type(right) != float):
            right = TFTamiltoEng(right)
        elif type(right) == int and (type(left) != int and type(left) != float):
            left = TFTamiltoEng(left)
        else:
            left = TFTamiltoEng(left)
            right = TFTamiltoEng(right)
        operator = logical_node.op
        # AND, OR
        if operator == 'AND':
            val = (left and right)
        elif operator == 'OR':
            val = (left or right)
        return TFEngtoTamil(val)
    
    # method to handle import statement
    def importModules(self, imp_node):
        modules_to_import = imp_node.modules_to_import
        for module in modules_to_import:
            [module_symbol_table, module_declared_funcs] = AramImport.load_module(module)
            self.SYMBOL_TABLE.update(module_symbol_table)
            self.DECLARED_FUNCTIONS.update(module_declared_funcs)
        return
    
    # method to handle conditional statement (if, elif, else)
    def conditionalStatement(self, cond_node):
        ifcases = cond_node.ifcases
        elsecase = cond_node.elsecase
        isAnyIfTrue = False
        # checking if return break or continue is used outside of a loop or function
        #return - கொடு
        #break - உடை 
        #continue - தொடர் 
        for i in ifcases:
            for j in i[1]:
                if type(j) == AramParser.ReturnNode and not self.insideFunction:
                    error.Error("செய் வெளியே பயன்பாடு", "கொடு")
                    self.hasErrored = True
                     
                elif type(j) == AramParser.BreakNode and self.insideLoop != True:
                    error.Error("Loopயின் வெளியே பயன்பாடு", "உடை")
                    self.hasErrored = True
                     
                elif type(j) == AramParser.ContinueNode and self.insideLoop != True:
                    error.Error("Loopயின் வெளியே பயன்பாடு", "தொடர்")
                    self.hasErrored = True
                     
        if elsecase != None:
            for i in elsecase:
                if type(i) == AramParser.ReturnNode and not self.insideFunction:
                    error.Error("செய் வெளியே பயன்பாடு", "கொடு")
                    self.hasErrored = True
                     
                elif type(i) == AramParser.BreakNode and self.insideLoop != True:
                    error.Error("Loopயின் வெளியே பயன்பாடு", "உடை")
                    self.hasErrored = True
                     
                elif type(i) == AramParser.ContinueNode and self.insideLoop != True:
                    error.Error("Loopயின் வெளியே பயன்பாடு", "தொடர்")
                    self.hasErrored = True
                     

        for i in ifcases:
            evalCond = self.visitNode(i[0])
            if type(evalCond) == int or type(evalCond) == float:
                if evalCond != 0:
                    evalCond = True
                else:
                    evalCond = False
            else:
                evalCond = TFTamiltoEng(evalCond)
            if type(evalCond) == int:
                if evalCond > 0:
                    evalCond = True
                else:
                    evalCond = False
            if evalCond:
                isAnyIfTrue = True
                for j in i[1]:
                    if self.breakLoop and self.insideLoop:
                        return
                    if type(j) == AramParser.ReturnNode:
                        if self.insideFunction:
                            out = self.return_statement(j)
                            if out != None:
                                res = self.visitNode(out)
                                return res
                            else:
                                return 'None'
                        else:
                            error.Error("செய் வெளியே பயன்பாடு", "கொடு")
                            self.hasErrored = True
                             
                    elif type(j) == AramParser.ConditionalNode or type(j) == AramParser.ForNode or type(j) == AramParser.WhileNode:
                        res = self.visitNode(j)
                        if res != None:
                            return res
                    elif type(j) == AramParser.BreakNode and self.insideLoop == True:
                        self.breakLoop = True
                        return 'None' 
                    elif type(j) == AramParser.BreakNode and self.insideLoop != True:
                        error.Error("Loopயின் வெளியே பயன்பாடு", "உடை")
                        self.hasErrored = True
                         
                    elif type(j) == AramParser.ContinueNode and self.insideLoop == True:
                        self.continueLoop = True
                        return 'None' 
                    elif type(j) == AramParser.ContinueNode and self.insideLoop != True:
                        error.Error("Loopயின் வெளியே பயன்பாடு", "தொடர்")
                        self.hasErrored = True
                         
                    else:
                        self.visitNode(j) 
                return
        if not isAnyIfTrue:
            if elsecase == None:
                return
            for i in elsecase:
                if self.breakLoop and self.insideLoop:
                    return
                if type(i) == AramParser.ReturnNode:
                    if self.insideFunction:
                        out = self.return_statement(i)
                        if out != None:
                            res = self.visitNode(out)
                            return res
                        else:
                            return 'None'
                    else:
                        error.Error("செய் வெளியே பயன்பாடு", "கொடு")
                        self.hasErrored = True
                         
                elif type(i) == AramParser.ConditionalNode or type(i) == AramParser.ForNode or type(i) == AramParser.WhileNode:
                    res = self.visitNode(i)
                    if res != None:
                        return res
                elif type(i) == AramParser.BreakNode and self.insideLoop == True:
                    self.breakLoop = True
                    return 'None' 
                elif type(i) == AramParser.BreakNode and self.insideLoop != True:
                    error.Error("Loopயின் வெளியே பயன்பாடு", "உடை")
                    self.hasErrored = True
                     
                elif type(i) == AramParser.ContinueNode and self.insideLoop == True:
                    self.continueLoop = True
                    return 'None' 
                elif type(i) == AramParser.ContinueNode and self.insideLoop != True:
                    error.Error("Loopயின் வெளியே பயன்பாடு", "தொடர்")
                    self.hasErrored = True
                     
                else:
                    self.visitNode(i)
            return
    
    # method to handle for statement
    def forStatement(self, for_node):
        times = self.visitNode(for_node.times_to_loop)
        statements_to_loop = for_node.repeatStatements
        self.insideLoop = True
        self.breakLoop = False
        self.continueLoop = False
        if type(times) == int and times > 0:
            for i in range(times):
                for j in statements_to_loop:
                    if self.breakLoop:
                        self.insideLoop = False
                        return 'None'
                    elif type(j) == AramParser.ReturnNode:
                        if self.insideFunction:
                            out = self.return_statement(j)
                            if out != None:
                                res = self.visitNode(out)
                                self.insideLoop = False
                                self.breakLoop = True
                                return res
                            else:
                                self.insideLoop = False
                                self.breakLoop = True
                                return 'None'
                        else:
                            error.Error("செய் வெளியே பயன்பாடு", "கொடு")
                            self.hasErrored = True
                             
                    elif type(j) == AramParser.ConditionalNode:
                        res = self.visitNode(j)
                        if self.continueLoop:
                            self.continueLoop = False
                            break
                        if res != None:
                            self.insideLoop = False
                            self.breakLoop = True
                            return res
                        if self.breakLoop:
                            self.breakLoop = False
                            self.insideLoop = False
                            return 'None'
                    elif type(j) == AramParser.ForNode or type(j) == AramParser.WhileNode:#add
                        res = self.visitNode(j)
                        self.breakLoop = False
                        self.insideLoop = True
                        self.continueLoop = False
                        if res != 'None':
                            self.insideLoop = False
                            self.breakLoop = True
                            return res
                    elif type(j) == AramParser.BreakNode:
                        self.breakLoop = True
                        self.insideLoop = False
                        return 'None'
                    elif type(j) == AramParser.ContinueNode:
                        break
                    else:
                        self.visitNode(j)
        elif type(times) == int and times <= 0:
            self.insideLoop = False
            self.breakLoop = True
            return
        else:
            error.Error("'சுற்று()' உள் முழுஎண் எதிர்பார்க்கப்பட்டது")
        self.insideLoop = False
        #self.breakLoop = True
        self.breakLoop = False
        return
    
    # method to handle while statement
    def whileStatement(self, while_node):
        repeatStatements = while_node.repeatStatements
        self.insideLoop = True
        self.breakLoop = False
        self.continueLoop = False
        #while (self.breakLoop != True):
        while (True):
            condition = self.visitNode(while_node.condition)
            if type(condition) == str:
                condition = TFTamiltoEng(condition)
            if condition:
                for i in repeatStatements:
                    if type(i) == AramParser.ReturnNode:
                        if self.insideFunction:
                            out = self.return_statement(i)
                            if out != None:
                                res = self.visitNode(out)
                                self.insideLoop = False
                                return res
                            else:
                                self.insideLoop = False
                                return 'None'
                        else:
                            error.Error("செய் வெளியே பயன்பாடு", "கொடு")
                            self.hasErrored = True
                             
                    elif type(i) == AramParser.ConditionalNode:
                        res = self.visitNode(i)
                        if self.continueLoop:
                            self.continueLoop = False
                            break
                        if self.breakLoop:
                            self.breakLoop = False
                            self.insideLoop = False
                            return 'None'
                        if res != None:
                            self.insideLoop = False
                            return res
                        if self.breakLoop:
                            self.insideLoop = False
                            return 'None'
                    elif type(i) == AramParser.ForNode or type(i) == AramParser.WhileNode:
                        res = self.visitNode(i)
                        self.breakLoop = False
                        self.insideLoop = True
                        self.continueLoop = False
                        if res != 'None':
                            print(res)
                            self.insideLoop = False
                            return res
                    elif type(i) == AramParser.BreakNode:
                        self.breakLoop = True
                        self.insideLoop = False
                        return 'None'
                    elif type(i) == AramParser.ContinueNode:
                            break
                    else:
                        self.visitNode(i)
            else:
                break
        self.insideLoop = False
        #self.breakLoop = True
        self.breakLoop = False
        return
    
    # method to handle return statement
    def return_statement(self, ret_node):
        returnVal = ret_node.returnVal
        return returnVal
    
    # method to handle function declaration
    def func_declaration(self, func_dec_node):
        func_name = func_dec_node.function_name
        self.DECLARED_FUNCTIONS[func_name] = func_dec_node
        return
    
    # method to handle a function call
    def func_call(self, func_call_node):
        func_name = func_call_node.func_name
        actual_params = func_call_node.actual_params
        #print('Passed:', actual_params, func_name)
        if func_name in self.DECLARED_FUNCTIONS:
            called_func = self.DECLARED_FUNCTIONS[func_name]
            if len(actual_params) != len(called_func.formal_params):
                err_msg = "தேவை" + str(called_func_params) + "parameters ஆனால் கொடுக்கப்படுள்ளது" + str(len(actual_params)) + "paramenters"
                error.Error(err_msg, str(func_name))
                self.hasErrored = True
                 
            res = self.execute_func(func_name, actual_params)
        elif func_name in self.BUILT_IN_FUNCTIONS:
            called_func_params = self.BUILT_IN_FUNCTIONS[func_name][0]
            if len(actual_params) != called_func_params:
                err_msg = "தேவை" + str(called_func_params) + "parameters ஆனால் கொடுக்கப்படுள்ளது" + str(len(actual_params)) + "paramenters"
                error.Error(err_msg, str(func_name))
                self.hasErrored = True
                 
            res = self.execute_builtin_func(func_name, actual_params)
        else:
            #print('Declared funcs:', self.DECLARED_FUNCTIONS)
            error.Error("அறிவிக்கப்படாத செய் அழைக்கப்பட்டுள்ளது", func_name)
            self.hasErrored = True
             
        return res
 
    # method to execute a function
    def execute_func(self, func_name, actual_parameters):
        self.insideFunction = True
        called_func = self.DECLARED_FUNCTIONS[func_name]
        if len(called_func.formal_params) != 0:
            for index, param in enumerate(called_func.formal_params):
                self.LOCAL_SCOPE_SYMBOL_TABLE[param.value] = self.visitNode(actual_parameters[index])
        func_statements = called_func.funcStatements
        #print('Local Scope:', self.LOCAL_SCOPE_SYMBOL_TABLE)
        #print(type(self.LOCAL_SCOPE_SYMBOL_TABLE['num1']))
        for i in func_statements:
            if type(i) == AramParser.ReturnNode:
                out = self.return_statement(i)
                if out != None:
                    res = self.visitNode(out)
                    self.insideFunction = False
                    self.LOCAL_SCOPE_SYMBOL_TABLE.clear()
                    return res
                else:
                    self.insideFunction = False
                    self.LOCAL_SCOPE_SYMBOL_TABLE.clear()
                    return 'None'
            elif type(i) == AramParser.ConditionalNode or type(i) == AramParser.ForNode or type(i) == AramParser.WhileNode:
                res = self.visitNode(i)
                if res != None:
                    self.insideFunction = False
                    self.LOCAL_SCOPE_SYMBOL_TABLE.clear()
                    return res
            elif type(i) == AramParser.BreakNode:
                error.Error("Loopயின் வெளியே பயன்பாடு", "உடை")
                self.insideFunction = False
                self.hasErrored = True
                 
            elif type(i) == AramParser.ContinueNode:
                error.Error("Loopயின் வெளியே பயன்பாடு", "தொடர்")
                self.insideFunction = False
                self.hasErrored = True
                 
            else:
                self.visitNode(i)
        self.LOCAL_SCOPE_SYMBOL_TABLE.clear()
        self.insideFunction = False
        return
    
    # method to execute builtin functions
    def execute_builtin_func(self, func_name, actual_params):
        evaluated_params = [self.visitNode(p) for p in actual_params]
        
        # ADD 'இடைச்செருகு' TO THIS CONDITION
        if func_name in ( 'உறுப்பு_சேர்', 'நீக்கு', 'இடைச்செருகு'):
            if len(actual_params) == 2: # For சேர் and நீக்கு
                 return self.BUILT_IN_FUNCTIONS[func_name][1](actual_params[0], evaluated_params[1])
            elif len(actual_params) == 3: # For இடைச்செருகு
                 return self.BUILT_IN_FUNCTIONS[func_name][1](actual_params[0], evaluated_params[1], evaluated_params[2])
        
        return self.BUILT_IN_FUNCTIONS[func_name][1](*evaluated_params)
    
    # method to execute corresponding methods depending on the type of object
    def visitNode(self, visit_node):
        node_type = type(visit_node)
        if node_type == AramParser.BinOpNode:
            return self.binaryOperator(visit_node)
        if node_type == AramParser.ConditionalNode:
            return self.conditionalStatement(visit_node)
        elif node_type == AramParser.NumberNode:
            return self.numberValue(visit_node)
        elif node_type == AramParser.StringNode:
            return self.stringValue(visit_node)
        elif node_type == AramParser.UnaryOpNode:
            return self.unaryValue(visit_node)
        elif node_type == AramParser.Assignment:
            return self.assignStatement(visit_node)
        elif node_type == AramParser.PrintNode:
            return self.printValue(visit_node)
        elif node_type == AramParser.Variable:
            return self.variableValue(visit_node)
        elif node_type == AramParser.InputNode:
            return self.inputValue(visit_node)
        elif node_type == AramParser.CompOpNode:
            return self.comparisonOperator(visit_node)
        elif node_type == AramParser.LogicalOpNode:
            return self.logicalOperator(visit_node)
        elif node_type == AramParser.ForNode:
            return self.forStatement(visit_node)
        elif node_type == AramParser.WhileNode:
            return self.whileStatement(visit_node)
        elif node_type == AramParser.FunctionNode:
            return self.func_declaration(visit_node)
        elif node_type == AramParser.Func_Call_Statement:
            return self.func_call(visit_node)
        elif node_type == AramParser.ReturnNode:
            return self.return_statement(visit_node)
        elif node_type == AramParser.ListNode:
            return self.listNode(visit_node)
        elif node_type == AramParser.ListIndexNode:
            return self.listIndexValue(visit_node)
        elif node_type == AramParser.ImportNode:
            return self.importModules(visit_node)
        elif node_type == AramParser.TryCatchNode:
            return self.tryCatchStatement(visit_node)
        elif node_type == AramParser.TupleIndexNode:
            return self.tupleIndexValue(visit_node)
        else:
            return "தொகுக்க முடியவில்லை! (codeல் பிழை உள்ளதா என சரிபார்க்கவும்)"
    
    def உறுப்பு_சேர்(self, variable_node, element_to_add):
        if not isinstance(variable_node, AramParser.Variable):
            error.Error("உறுப்பு_சேர்() expects a variable as its first argument.")
            self.hasErrored = True
            return None
        var_name = variable_node.value
        actual_collection = self.SYMBOL_TABLE.get(var_name) or self.LOCAL_SCOPE_SYMBOL_TABLE.get(var_name)
        if actual_collection is None:
            error.Error(f"Variable '{var_name}' not found.")
            self.hasErrored = True
            return None
        if isinstance(actual_collection, list):
            actual_collection.append(element_to_add)
        elif isinstance(actual_collection, set):
            actual_collection.add(element_to_add)
        else:
            error.Error(f"The variable '{var_name}' is not a list or a set.")
            self.hasErrored = True
        return None

    def நீக்கு(self, variable_node, element_to_remove):
        if not isinstance(variable_node, AramParser.Variable):
            error.Error("நீக்கு() expects a variable as its first argument.")
            self.hasErrored = True
            return None
        var_name = variable_node.value
        actual_collection = self.SYMBOL_TABLE.get(var_name) or self.LOCAL_SCOPE_SYMBOL_TABLE.get(var_name)
        if actual_collection is None:
            error.Error(f"Variable '{var_name}' not found.")
            self.hasErrored = True
            return None
        if isinstance(actual_collection, list):
            try:
                actual_collection.remove(element_to_remove)
            except ValueError:
                error.Error(f"Element '{element_to_remove}' not found in the list.")
                self.hasErrored = True
        elif isinstance(actual_collection, set):
            try:
                actual_collection.remove(element_to_remove)
            except KeyError:
                error.Error(f"Element '{element_to_remove}' not found in the set.")
                self.hasErrored = True
        else:
            error.Error(f"The variable '{var_name}' is not a list or a set.")
            self.hasErrored = True
        return None
    def இடைச்செருகு(self, variable_node, index, element):
        if not isinstance(variable_node, AramParser.Variable):
            error.Error("இடைச்செருகு() expects a variable as its first argument.")
            self.hasErrored = True
            return None
        
        var_name = variable_node.value
        actual_list = self.SYMBOL_TABLE.get(var_name) or self.LOCAL_SCOPE_SYMBOL_TABLE.get(var_name)
        
        if actual_list is None:
            error.Error(f"Variable '{var_name}' not found.")
            self.hasErrored = True
            return None
        if not isinstance(actual_list, list):
            error.Error(f"The variable '{var_name}' is not a list.")
            self.hasErrored = True
            return None
        if not isinstance(index, int):
            error.Error("Index must be an integer for இடைச்செருகு().")
            self.hasErrored = True
            return None
        
        actual_list.insert(index, element)
        return None
    def tryCatchStatement(self, node):
        """
        Executes a try-catch-finally block.
        """
        try:
            # Execute the 'try' block
            for statement in node.try_block:
                self.visitNode(statement)
        except Exception as e:
            # If an exception occurs, execute the 'except' block if it exists
            if node.except_block:
                if node.except_var:
                    # Assign the error message to the specified variable
                    error_message = str(e).strip()
                    if self.insideFunction:
                        self.LOCAL_SCOPE_SYMBOL_TABLE[node.except_var] = error_message
                    else:
                        self.SYMBOL_TABLE[node.except_var] = error_message
                
                # Execute statements in the except block
                for statement in node.except_block:
                    self.visitNode(statement)
        finally:
            # Execute the 'finally' block if it exists, regardless of exceptions
            if node.finally_block:
                for statement in node.finally_block:
                    self.visitNode(statement)
        
        return None
    
    