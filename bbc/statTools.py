def ipFrac(i):
	if i == None:
		return 0
	return int(round((float(i)-round(float(i)))*10,0))


def addIP(i1,i2):
	if i1 == None:
		return i2
	if i2 == None:
		return i1
	ipf1 = ipFrac(i1)
	ipf2 = ipFrac(i2)
	ipf = ipf1+ipf2
	if ipf == 0:
		return (float(i1)+float(i2))
	if ipf == 1:
		return float(i1)+float(i2)
	if ipf == 2:
		return float(i1)+float(i2)
	if ipf == 3:
		return float(i1)+float(i2)+1-.3
	if ipf == 4:
		return float(i1)+float(i2)+1-.3

def ipToOuts(ip):
	return int(round(float(ip))) * 3 + ipFrac(ip)