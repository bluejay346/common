#!/usr/bin/python

import requests, argparse, json, sys

class BTCGuildError(Exception):
  def __init__(self, value):
    self.msg = value
  def __str__(self):
    return self.msg

def parseArgs():

  parser = argparse.ArgumentParser(description="Tool to pull cacti stats out of ASICMiner Blades (v2)")
  parser.add_argument("--apikey",  metavar="<key", help="Your API Key from BTC Guild", required=True)
  parser.add_argument("--items", metavar="<xx,xx,..>", help="List of items, comma separated", required=True)

  return parser.parse_args()

def getInfo(apikey, timeout=0.75):
  result = None
  try:
    URL = "https://www.btcguild.com/api.php?api_key=%s" % (apikey) 
    result = requests.get(URL, timeout=timeout)
  except requests.ConnectionError, err:
    raise BTCGuildError("Could not connect to web port: %s" % err.message)
  except requests.HTTPError, err:
    raise BTCGuildError("Invalid HTTP Response: %s" % err.message)
  except (requests.Timeout, socket.timeout), err:
    raise BTCGuildError("Timed out connecting")

  return result

def sumWorkerField(workers, fieldName):
  sum = 0
  for worker in workers.keys():
    sum += workers[worker][fieldName]
  return sum

def main():

  userInfo  = None
  args      = parseArgs()

  try:
    userInfo = getInfo(args.apikey)
  except BTCGuildError, err:
    print "Error Getting Info: %s" % err.msg
    return False

  try:
    u = json.loads(userInfo.content)
  except (ValueError, TypeError), err:
    print "Error interpreting result: %s" % err.message
    return False

  validItems = {
    "ps": u["pool"]["pool_speed"],
    "df": u["pool"]["difficulty"],
    "tr": u["user"]["total_rewards"],
    "ur": u["user"]["unpaid_rewards"],
    "pr": u["user"]["paid_rewards"],
    "24": u["user"]["past_24h_rewards"],
    "ds": sumWorkerField(u["workers"], "dupe_shares"),
    "us": sumWorkerField(u["workers"], "unknown_shares"),
    "ss": sumWorkerField(u["workers"], "stale_shares"),
    "vs": sumWorkerField(u["workers"], "valid_shares"),
    "hr": sumWorkerField(u["workers"], "hash_rate")
  }

  pad = ''
  for item in args.items.split(","):
    if item in validItems.keys():
      sys.stdout.write("%s%s:%s" % ( pad, item, validItems[item]))
      pad = ' '

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    print "CTRL-C"

