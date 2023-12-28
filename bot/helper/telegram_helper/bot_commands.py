from bot import CMD_SUFFIX


class _BotCommands:
    def __init__(self):
        self.StartCommand = f"start{CMD_SUFFIX}"
        self.MirrorCommand = [f"mirror{CMD_SUFFIX}", f"m{CMD_SUFFIX}"]
        self.QbMirrorCommand = [f"qbmirror{CMD_SUFFIX}", f"qm{CMD_SUFFIX}"]
        self.JdMirrorCommand = [f"jdmirror{CMD_SUFFIX}", f"jm{CMD_SUFFIX}"]
        self.YtdlCommand = [
            f"ytdl{CMD_SUFFIX}", f"y{CMD_SUFFIX}", f"watch{CMD_SUFFIX}", f"w{CMD_SUFFIX}"]
        self.LeechCommand = [f"leech{CMD_SUFFIX}", f"l{CMD_SUFFIX}"]
        self.QbLeechCommand = [f"qbleech{CMD_SUFFIX}", f"ql{CMD_SUFFIX}"]
        self.JdLeechCommand = [f"jdleech{CMD_SUFFIX}", f"jl{CMD_SUFFIX}"]
        self.YtdlLeechCommand = [
            f"ytdlleech{CMD_SUFFIX}", f"yl{CMD_SUFFIX}", f"watchleech{CMD_SUFFIX}", f"wl{CMD_SUFFIX}"]
        self.CloneCommand = [f"clone{CMD_SUFFIX}", f"cl{CMD_SUFFIX}"]
        self.CountCommand = [f"count{CMD_SUFFIX}", f"co{CMD_SUFFIX}"]
        self.DeleteCommand = [f"delete{CMD_SUFFIX}", f"del{CMD_SUFFIX}"]
        self.CancelTaskCommand = [f"cancel{CMD_SUFFIX}", f"c{CMD_SUFFIX}"]
        self.CancelAllCommand = [f"cancelall{CMD_SUFFIX}", f"ca{CMD_SUFFIX}"]
        self.ListCommand = [f"list{CMD_SUFFIX}", f"li{CMD_SUFFIX}"]
        self.SearchCommand = [f"search{CMD_SUFFIX}", f"se{CMD_SUFFIX}"]
        self.StatusCommand = [f"status{CMD_SUFFIX}", f"sta{CMD_SUFFIX}"]
        self.UsersCommand = [f"users{CMD_SUFFIX}", f"us{CMD_SUFFIX}"]
        self.AuthorizeCommand = [f"authorize{CMD_SUFFIX}", f"au{CMD_SUFFIX}"]
        self.UnAuthorizeCommand = [
            f"unauthorize{CMD_SUFFIX}", f"ua{CMD_SUFFIX}"]
        self.AddSudoCommand = [f"addsudo{CMD_SUFFIX}", f"as{CMD_SUFFIX}"]
        self.RmSudoCommand = [f"rmsudo{CMD_SUFFIX}", f"rs{CMD_SUFFIX}"]
        self.PingCommand = [f"ping{CMD_SUFFIX}", f"p{CMD_SUFFIX}"]
        self.RestartCommand = [f"restart{CMD_SUFFIX}", f"r{CMD_SUFFIX}"]
        self.StatsCommand = [f"stats{CMD_SUFFIX}", f"sts{CMD_SUFFIX}"]
        self.HelpCommand = [f"help{CMD_SUFFIX}", f"h{CMD_SUFFIX}"]
        self.LogCommand = [f"log{CMD_SUFFIX}", f"lo{CMD_SUFFIX}"]
        self.ShellCommand = [f"shell{CMD_SUFFIX}", f"sh{CMD_SUFFIX}"]
        self.SpeedCommand = [f"speedtest{CMD_SUFFIX}", f"sp{CMD_SUFFIX}"]
        self.EvalCommand = [f"eval{CMD_SUFFIX}", f"ev{CMD_SUFFIX}"]
        self.ExecCommand = [f"exec{CMD_SUFFIX}", f"ex{CMD_SUFFIX}"]
        self.ClearLocalsCommand = [f"clearlocal{CMD_SUFFIX}", f"clo{CMD_SUFFIX}"]
        self.BotSetCommand = [f"bsetting{CMD_SUFFIX}", f"bset{CMD_SUFFIX}", f"bs{CMD_SUFFIX}"]
        self.UserSetCommand = [f"usetting{CMD_SUFFIX}", f"uset{CMD_SUFFIX}", f"us{CMD_SUFFIX}"]
        self.BtSelectCommand = [f"btsel{CMD_SUFFIX}", f"bts{CMD_SUFFIX}"]
        self.RssCommand = f"rss{CMD_SUFFIX}"


BotCommands = _BotCommands()
