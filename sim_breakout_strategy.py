__author__ = 'prashant'

import sys

f = open("DAT_ASCII_EURUSD_M1_2000_2015.csv", "r")
fo = open("DAT_ASCII_EURUSD_M1_2000_2015_results.csv", "w")

cur_date = None
cur_high = None
cur_low = None

oco_buy = None
oco_sell = None
oco_set = False
oco_triggered = False
oco_sold = False
oco_type = None
cnt_buy = 0
cnt_sell = 0
cnt_buy_sell = 0
cnt_profit = 0
cnt_loss = 0
cnt_floss = 0

handle_later = False
do_nothing = False

profit = 0.0010

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

    if oco_triggered and not oco_sold:
      fo.write( "Force Loss," + "-9999999" + "," + "-999999" + "\n")

    cur_date = val_date
    cur_high = None
    cur_low = None
    oco_buy = None
    oco_sell = None
    oco_set = False
    oco_triggered = False
    oco_sold = False
    oco_type = None
    handle_later = False

  elif handle_later:
    continue

  # while we're figuring out the 3AM 10 minute candle hi and lo
  elif val_time >= "030000" and val_time <= "031000":
    cur_high = val_high if (cur_high is None or val_high > cur_high) else cur_high
    cur_low  = val_low if (cur_low is None or val_low < cur_low) else cur_low
    if val_time == "031000":
      #print "hilo for ", cur_date, " are ", cur_high, " and ", cur_low
      oco_buy = cur_high + .0010
      oco_sell = cur_low - .0010
      oco_set = True
      oco_triggered = False
      fo.write(cur_date + "," + "{0:1.6f}".format(oco_buy) + "," +  "{0:1.6f}".format(oco_sell) + ",")

  # Figure out when the OCO order will trigger.
  elif val_time > "031100" and oco_set and not oco_triggered:
    if val_high >= oco_buy and val_low <= oco_sell:
      # oco_triggered = True
      oco_triggered = True
      handle_later = True
      fo.write( "Buy_Sell" + "," + val_time + ",")
    elif val_high >= oco_buy:
      oco_triggered = True
      oco_type = "buy"
      fo.write("Buy" + "," + val_time + ",")
    elif val_low <= oco_sell:
      oco_triggered = True
      oco_type = "sell"
      fo.write( "Sell" + "," + val_time + ",")

  # Once OCO triggered, figure out what time profit-taking limit triggers
  elif oco_set and oco_triggered and not oco_sold:
    if oco_type == "sell":
      target_price = oco_sell - profit
      if val_high >= oco_buy:
        oco_sold = True
        fo.write("Loss," + "{0:1.6f} ".format(target_price) + "," + val_time + "\n")
      elif  val_low < target_price:
        fo.write("Profit," + "{0:1.6f} ".format(target_price) + "," + val_time + "\n")
        oco_sold = True
      else:
        do_nothing
    elif oco_type == "buy":
      target_price = oco_buy + profit
      if val_low <= oco_sell:
        oco_sold = True
        fo.write("Loss," + "{0:1.6f} ".format(target_price) + "," + val_time + "\n")
      elif val_high > target_price:
        fo.write( "Profit," + "{0:1.6f} ".format(target_price)+","+ val_time + "\n")
        oco_sold = True
      else:
        do_nothing
    else:
      fo.write( "Force Loss," + "-9999999" + "," + "-999999" + "\n")

f.close()
fo.close()

#Open the results file to analyze

f = open("DAT_ASCII_EURUSD_M1_2000_2015_results.csv", "r")
for line in f:
  items = line.split(',')
  val_date = float(items[0])
  val_buy = items[1]
  val_sell = items[2]
  val_action = items[3]
  val_action_time  = items[4]
  val_result = items[5]
  val_clos_prc = items[6]
  val_clos_time = items[7]


  if val_action == "Buy":
     cnt_buy = cnt_buy + 1
  elif val_action == "Sell":
     cnt_sell = cnt_sell + 1
  elif val_action == "Buy_Sell":
     cnt_buy_sell = cnt_buy_sell + 1

  if val_result == "Profit":
      cnt_profit = cnt_profit + 1
  elif val_result == "Loss":
      cnt_loss = cnt_loss + 1
  elif val_result == "Force Loss":
      cnt_floss = cnt_floss + 1

print("No of Buys:%d" %(cnt_buy))
print("No of Sells:%d" %(cnt_sell))
print("No of Buys_Sells:%d" %(cnt_buy_sell))
print("No of profitable trades:%d" %(cnt_profit))
print("No of Non-Profitable trades:%d" %(cnt_loss))
print("No of Force Closed trades:%d" %(cnt_floss))

f.close()
