def second2hhmmss(s):
    h = s / 3600
    m = (s % 3600) / 60
    s = s % 60
    return "%02dh%02dm%02ds" % (h, m, s)

if __name__ == '__main__':
    print(second2hhmmss(112416.39))