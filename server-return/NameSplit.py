def nameSplit(tosplit) :
  last = 0
  splits = []
  inQuote = None
  for i, letter in enumerate(tosplit) :
    if inQuote :
      if (letter == inQuote) :
        inQuote = None
    else :
      if (letter == '"' or letter == "'") :
        inQuote = letter

    if not inQuote and letter == ' ' :
      splits.append(tosplit[last:i])
      last = i+1

  if last < len(tosplit) :
    splits.append(tosplit[last:])

  return splits
