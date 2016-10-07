from multi_key_dict import multi_key_dict

XWSL_CMD_CMODES = multi_key_dict()
XWSL_CMD_CMODES[0, "r", "run"]       = "~r"
XWSL_CMD_CMODES[1, "c", "cmd"]       = "~c"
XWSL_CMD_CMODES[2, "s", "start"]     = "~s"

XWSL_RESP_MODES = multi_key_dict()
XWSL_RESP_RMODES[3, "a", "ack"]      = "!A"
XWSL_RESP_RMODES[4, "d", "data"]     = "!d"
XWSL_RESP_RMODES[5, "b", "bytesize"] = "!b"

XWSL_MODIFIERS = {
    XWSL_CMD_CMODES["run"]:         "run",
    XWSL_CMD_CMODES["cmd"]:         "cmd",
    XWSL_CMD_CMODES["start"]:       "start",
    XWSL_RESP_RMODES["ack"]:        "ack",
    XWSL_RESP_RMODES["data"]:       "data",
    XWSL_RESP_RMODES["bytesize"]:   "bytesize",
}

XWSL_RECV_SIZES = multi_key_dict()
XWSL_RECV_SIZES[0, "r", "run", XWSL_CMD_CMODES[0]]       = 3072
XWSL_RECV_SIZES[1, "c", "cmd", XWSL_CMD_CMODES[1]]       = 3072
XWSL_RECV_SIZES[2, "s", "start", XWSL_CMD_CMODES[2]]     = 3072
XWSL_RECV_SIZES[3, "a", "ack", XWSL_RESP_RMODES[3]]      = 64
XWSL_RECV_SIZES[4, "d", "data", XWSL_RESP_RMODES[4]]     = -1 # variable
XWSL_RECV_SIZES[5, "b", "bytesize", XWSL_RESP_RMODES[5]] = 256

for i in range(len(XWSL_RECV_SIZES)):
    XWSL_RECV_SIZES[i] += 1 # 1 over size limit


class SOCK:
    DEFAULT_SERVER      = ('localhost', 15579)
    MAX_LISTENS         = 5
    DEFAULT_MODE        = "cmd"






