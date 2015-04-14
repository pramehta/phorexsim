import sys

f = open("DAT_ASCII_EURUSD_M1_201504.csv", "r")

cur_date = None
cur_high = None
cur_low = None

oco_buy = None
oco_sell = None
oco_triggered = None

for line in f:
  items = line.split()
  val_date = items[0]
  val_time = items[1]
  val_open = float(items[2])
  val_high = float(items[3])
  val_low  = float(items[4])
  val_clos = float(items[5])

  # If we've moved to the next day
  if val_date != cur_date:
    cur_date = val_date

  # while we're figuring out the 3AM 10 minute candle hi and lo
  elif val_time >= "030000" and val_time <= "031000":
    cur_high = val_high if (cur_high is None or val_high > cur_high) else cur_high
    cur_low  = val_low if (cur_low is None or val_low < cur_low) else cur_low
    if val_time == "031000":
      print "hilo for ", cur_date, " are ", cur_high, " and ", cur_low
      oco_sell = cur_high + .000010
      oco_buy = cur_low - 0.000010
      oco_triggered = False
      print "OCO: ", oco_sell, oco_buy
      cur_high = None
      cur_low = None

  # Figure out when the OCO order will trigger
  elif val_time > "031000" and not oco_triggered:
    if val_high >= oco_sell and val_low <= oco_buy:
      oco_triggered = True
      print "OCO sell AND buy triggered together"
    elif val_high >= oco_sell:
      oco_triggered = True
      print "OCO sell triggered at ", val_time
    elif val_low <= oco_buy:
      oco_triggered = True
      print "OCO buy triggered at ", val_time

