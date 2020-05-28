"""

"""

import docstringer

netpyne_functions = docstringer.get_all_functions('netpyne')
netpyne_classes = docstringer.get_all_classes('netpyne')

print()
print('functions')
print('==================================')
for function in netpyne_functions:
    print(function)
print()
print()
print('classes')
print('==================================')
for classi in netpyne_classes:
    print(classi)
print()
print()
print()
print()
print()


# Success!!
# % cdn ; cd doc ; ipython -i docstringer.py

# So, need to make it into an importable package right away
# Subpackages: 'get', 




# '''
# Modularize the code
#     doc_dict_from_module
#     parse_docstring
#     use_old_docstring
#     write_docstring 
#     replace docstring
#     main function

# Look into auto-getting all functions/classes

# Dealing with classes
#     Need to document class methods
#     Need to format output for classes
#         Need to remove return, return_type, examples from classes

# Create GitHub issues with copy of original docstrings

# Go through Sphinx warnings

# Fix See Also parentheses

# Make docstringer into a package?
# '''


