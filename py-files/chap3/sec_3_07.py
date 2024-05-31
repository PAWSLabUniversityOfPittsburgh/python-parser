prompt ="What is the air velocity of an unladen swallow?\n"
speed =input(prompt)

int(speed)

inp =input('Enter Fahrenheit Temperature: ')
fahr =float(inp)
cel =(fahr -32.0)*5.0 /9.0
print(cel)

inp =input('Enter Fahrenheit Temperature:')
try:
    fahr =float(inp)
    cel =(fahr -32.0)*5.0 /9.0
    print(cel)
except:
    print('Please enter a number')
    

