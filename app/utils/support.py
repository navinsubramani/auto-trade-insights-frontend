
# Define a function to apply color based on conditions
def color_cells(value):
    if value > 0.5:
        color = 'background-color: green'
    elif value > 0.1:
        color = 'background-color: lightgreen'
    elif value < -0.5:
        color = 'background-color: red'
    elif color < -0.1:
        color = 'background-color: lightcoral'
    else:
        color = 'background-color: white'
    return color