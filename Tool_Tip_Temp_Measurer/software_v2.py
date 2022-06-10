# Importing necessary modules
from tkinter import (
    Tk,
    Scrollbar,
    Button,
    Label,
    Listbox,
    StringVar,
    Entry,
    END,
    Frame,
    messagebox,
    Frame,
)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import time 
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from datetime import datetime, time
from csv import writer
import matplotlib.dates as mdates
from backend import backend
import math
import pandas as pd


delta = 0
times = []
temperatures = []

# Creating a window
root = Tk()
root.configure(bg="#b2b2be")
# Title for root
root.wm_title("Tool-Tip-Temperature Measurer")

window = Frame(root, width=300, height=300)
window.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))


def plotInit():
    global line
    global fig
    global ax
    # Setting figure sizes
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams["figure.figsize"] = (6, 4)
    plt.rcParams.update(
        {
            "figure.facecolor": (1.0, 1.0, 1.0, 0.0),  # red   with alpha = 30%
            "axes.facecolor": (1.0, 1.0, 1.0, 0.0),  # green with alpha = 50%
            "savefig.facecolor": (1.0, 1.0, 1.0, 0.0),  # blue  with alpha = 20%
        }
    )

    fig = plt.figure()
    ax = fig.add_subplot()

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().grid(row=0, column=7, columnspan=3, rowspan=7)
    canvas.draw()

    # toolbarFrame = Frame(window)
    # toolbarFrame.grid(row=8, column=7, columnspan=3)
    # toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
    # toolbar.update()

    (line,) = plt.plot(times, temperatures, "r", marker="o")

    # Adding labels for the graph
    ax.set_xlabel("time")
    ax.set_ylabel("temperature(°C)")

    # Setting the x-axis formatter for date formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    plt.xticks(rotation=45, ha="right", rotation_mode="anchor")


def getSelectedMaterial(event):
    try:
        global selectedMaterial
        global id

        selection = materialList.curselection()

        # Checking for empty selection
        if not (len(selection) > 0):
            return

        # Getting id of the selected material
        data = materialList.get(selection[0])
        id = int(data.split(".")[0])

        # Getting material data from the database
        selectedMaterial = backend.use(id)[0]

        clearMaterialData()

        # Inserting data to corresponding inputs
        materialEntry.insert(END, selectedMaterial[1].capitalize())
        specificHeatCapacityEntry.insert(END, selectedMaterial[4])
        condutivityEntry.insert(END, selectedMaterial[2])
        densityEntry.insert(END, selectedMaterial[6])

    except IndexError as e:
        print(e, "get")
        messagebox.showerror("Error", e)


def clearInputs():
    # Removing text from the inputs
    cuttingForceEntry.delete(0, END)
    normalForceEntry.delete(0, END)
    ctRatioEntry.delete(0, END)
    rAngleEntry.delete(0, END)
    diameterEntry.delete(0, END)
    lengthEntry.delete(0, END)
    areaEntry.delete(0, END)
    speedEntry.delete(0, END)

    clearMaterialData()


def clearMaterialData():
    # Removing text from the inputs
    specificHeatCapacityEntry.delete(0, END)
    densityEntry.delete(0, END)
    condutivityEntry.delete(0, END)
    materialEntry.delete(0, END)


def useAllData():
    global delta
    # Getting input datas
    Fc = float(cuttingForce.get())
    Ft = float(normalForce.get())
    r = float(ctRatio.get())
    alpha = float(rAngle.get())
    D = float(diameter.get())
    N = float(speed.get())
    L = float(length.get())
    A = float(area.get())
    k = float(condutivity.get())

    if not (Fc == "" or Ft == "" or alpha == "" or r == "" or D == "" or N == ""):
        if k == "":
            messagebox.showwarning("Warning", "Please select material!")
            return

        try:
            # Cutting force(V = piDN/60000)
            V = math.pi * D * N / 60000

            # Chip velocity(Vc = rV)
            Vc = r * V

            # Frictional force(F = Fcsin(α) + Ftcos(α))
            F = Fc * math.sin(math.radians(alpha)) + Ft * math.cos(math.radians(alpha))

            # Heat lost due to friction
            Qf = F * Vc

            delta = Qf * L / (A * k)

            data = {
                "Cutting Force": [Fc],
                "Normal Force": [Ft],
                "Rake Angle": [alpha],
                "Diameter": [D],
                "Speed": [N],
                "Cutting Speed": [V],
                "Chip Velocity": [Vc],
                "Frictional Force": [F],
                "Heat due to friction": [Qf],
                "Area of cross-section of tool": [A],
                "Distance between two points": [L],
            }

            pd.DataFrame(data).T.to_csv(f"logs/data_{int(time.time())}.csv")

        except Exception as e:
            print(e, "data")
            messagebox.showerror("Error", e)
    else:
        messagebox.showwarning("Error", "Input/s can not be empty!")


def viewAllMaterials():
    appendMaterialsToList(backend.viewAll())


def appendMaterialsToList(materials):
    materialList.delete(0, END)

    # Chaking for empty list
    if len(materials) == 0:
        messagebox.showinfo("Not found!", "No material found!")
        return

    for material in materials:
        mat = str(material[0]) + ". " + str(material[1]).capitalize()
        materialList.insert(END, mat)


def searchMaterialData():
    data = backend.search(search.get())
    appendMaterialsToList(data)


# Getting data from serial
def getData():
    time.sleep(1.5)
    return arduino.readline().decode("utf-8").rstrip("\n\r")


# Writing data to the file
def writeToFile(data):
    with open("tool-tip-temperatures.csv", "a", newline="") as file:
        # Initializing the writer object with past temperatures
        writerObj = writer(file)

        # Writing new current temeprature
        writerObj.writerow(data)


# Function to update the plot
def update(arg):
    if delta == 0:
        return

    time = datetime.now().strftime("%H:%M:%S")
    data = getData()

    if len(data) > 0:
        T1, Tf2 = data.split(",")
        T2 = delta + float(T1)

        # Writing the current temperature to file
        writeToFile([time, T2, T1])

        times.append(time)
        temperatures.append(T2)

        plt.plot([datetime.strptime(t, "%H:%M:%S") for t in times], temperatures)


# Handling window-close event
def onCloseWindow():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        plt.close("all")
        root.destroy()


def gui():
    global root
    global window
    global cuttingForceEntry
    global cuttingForce
    global normalForceEntry
    global normalForce
    global rAngleEntry
    global rAngle
    global ctRatioEntry
    global ctRatio
    global specificHeatCapacityEntry
    global specificHeatCapacity
    global densityEntry
    global density
    global diameter
    global diameterEntry
    global speed
    global speedEntry
    global condutivityEntry
    global condutivity
    global material
    global materialEntry
    global materialList
    global search
    global area
    global areaEntry
    global length
    global lengthEntry
    global arduino

    ######################## Labels and inputs #####################################

    # Cutting force(Fc)
    # Label for cutting force
    cuttingForceLabel = Label(window, text="Cutting force(Fc)")
    cuttingForceLabel.grid(row=0, column=0)

    # Declaring string variable for cutting force
    cuttingForce = StringVar()

    # Input-box for cutting-force
    cuttingForceEntry = Entry(window, textvariable=cuttingForce)
    cuttingForceEntry.grid(row=0, column=1)

    # Normal force(Ft)
    normalForceLabel = Label(window, text="Normal force(Ft)")
    normalForceLabel.grid(row=0, column=2)

    normalForce = StringVar()
    normalForceEntry = Entry(window, textvariable=normalForce)
    normalForceEntry.grid(row=0, column=3)

    # Chip Thickness Ratio(r)
    ctRatioLabel = Label(window, text="Chip Thickness Ratio(r)")
    ctRatioLabel.grid(row=1, column=0)

    ctRatio = StringVar()
    ctRatioEntry = Entry(window, textvariable=ctRatio)
    ctRatioEntry.grid(row=1, column=1)

    # Rake angle(α)
    rAngleLabel = Label(window, text="Rake angle(α)")
    rAngleLabel.grid(row=1, column=2)

    rAngle = StringVar()
    rAngleEntry = Entry(window, textvariable=rAngle)
    rAngleEntry.grid(row=1, column=3)

    # Diameter(D)
    diameterLabel = Label(window, text="Diameter(D)")
    diameterLabel.grid(row=2, column=0)

    diameter = StringVar()
    diameterEntry = Entry(window, textvariable=diameter)
    diameterEntry.grid(row=2, column=1)

    # Speed(N)
    speedLabel = Label(window, text="Speed(N)")
    speedLabel.grid(row=2, column=2)

    speed = StringVar()
    speedEntry = Entry(window, textvariable=speed)
    speedEntry.grid(row=2, column=3)

    # Tool C-Area(A)
    areaLabel = Label(window, text="Tool C-Area(A)")
    areaLabel.grid(row=3, column=0)

    area = StringVar()
    areaEntry = Entry(window, textvariable=area)
    areaEntry.grid(row=3, column=1)

    # Length(L)
    lengthLabel = Label(window, text="Length(L)")
    lengthLabel.grid(row=3, column=2)

    length = StringVar()
    lengthEntry = Entry(window, textvariable=length)
    lengthEntry.grid(row=3, column=3)

    ###### Material data

    # Specific Heat Capacity(Cp)
    specificHeatCapacityLabel = Label(window, text="Specific Heat Capacity(Cp)")
    specificHeatCapacityLabel.grid(row=4, column=0)

    specificHeatCapacity = StringVar()
    specificHeatCapacityEntry = Entry(window, textvariable=specificHeatCapacity)
    specificHeatCapacityEntry.grid(row=4, column=1)

    # Thermal Conductivity(K
    condutivityLabel = Label(window, text="Thermal Conductivity(K)")
    condutivityLabel.grid(row=4, column=2)

    condutivity = StringVar()
    condutivityEntry = Entry(window, textvariable=condutivity)
    condutivityEntry.grid(row=4, column=3)

    # Density(ρ)
    densityLabel = Label(window, text="Density(ρ)")
    densityLabel.grid(row=5, column=0)

    density = StringVar()
    densityEntry = Entry(window, textvariable=density)
    densityEntry.grid(row=5, column=1)

    # Material
    materialLabel = Label(window, text="Material")
    materialLabel.grid(row=6, column=0)

    material = StringVar()
    materialEntry = Entry(window, textvariable=material)
    materialEntry.grid(row=6, column=1)

    # Search Bar
    searchLabel = Label(window, text="Search")
    searchLabel.grid(row=6, column=2)

    search = StringVar()
    searchEntry = Entry(window, textvariable=search)
    searchEntry.grid(row=6, column=3)

    ################### Buttons #########################
    useDataBtn = Button(window, text="Use Data", width=12, command=useAllData)
    useDataBtn.grid(row=5, column=2)

    clearBtn = Button(window, text="Clear", width=12, command=clearInputs)
    clearBtn.grid(row=5, column=3)

    searchBtn = Button(window, text="Search", width=12, command=searchMaterialData)
    searchBtn.grid(row=7, column=3)

    viewBtn = Button(
        window, text="View All Material", width=12, command=viewAllMaterials
    )
    viewBtn.grid(row=8, column=3)

    closeBtn = Button(window, text="Close", width=12, command=root.destroy)
    closeBtn.grid(row=9, column=3)

    #################### List-Box ##########################
    # List box for material details
    materialList = Listbox(window, height=10, width=50)
    materialList.grid(row=7, column=0, rowspan=6, columnspan=2)

    # Vertical-Scrollbar for listbox
    vScrollbar = Scrollbar(window)
    vScrollbar.grid(row=7, column=2, rowspan=8, columnspan=1)

    # Configuring the vertical-scrollbar for listbox as sselectBtn
    materialList.configure(yscrollcommand=vScrollbar.set)

    # Configuring vertical moment
    vScrollbar.configure(command=materialList.yview)

    materialList.bind("<<ListboxSelect>>", getSelectedMaterial)

    # for widget in window.winfo_children():
    #     widget.grid(padx=2, pady=2)

    # Adding custom event when window is closed
    root.protocol("WM_DELETE_WINDOW", onCloseWindow)

    try:
        # Configuring the serial port data
        arduino = serial.Serial(port="COM3", baudrate=9600, timeout=0.1)
    except Exception as e:
        plt.close("all")
        root.withdraw()
        messagebox.showerror("Error", "Could not connect to hardware")
        root.destroy()
        exit(0)


# Setting up GUI
gui()

plotInit()

# Graph animation(Live graph)
ani = anim.FuncAnimation(fig, update, interval=1000, blit=False)

# Run the GUI
root.mainloop()
