from bot import CMD_SUFFIX


class _BotCommands:
    def __init__(self):
        self.StartCommand = f'start{CMD_SUFFIX}'
        self.MirrorCommand = [f'mirror{CMD_SUFFIX}', f'm{CMD_SUFFIX}']
        self.UnzipMirrorCommand = [
            f'unzipmirror{CMD_SUFFIX}', f'uz{CMD_SUFFIX}']
        self.ZipMirrorCommand = [f'zipmirror{CMD_SUFFIX}', f'zm{CMD_SUFFIX}']
        self.QbMirrorCommand = [f'qbmirror{CMD_SUFFIX}', f'qb{CMD_SUFFIX}']
        self.QbUnzipMirrorCommand = [
            f'qbunzipmirror{CMD_SUFFIX}', f'qbuz{CMD_SUFFIX}']
        self.QbZipMirrorCommand = [
            f'qbzipmirror{CMD_SUFFIX}', f'qbz{CMD_SUFFIX}']
        self.YtdlCommand = [
            f'ytdl{CMD_SUFFIX}', f'y{CMD_SUFFIX}', f'watch{CMD_SUFFIX}', f'w{CMD_SUFFIX}']
        self.YtdlZipCommand = [
            f'ytdlzip{CMD_SUFFIX}', f'yz{CMD_SUFFIX}', f'zipwatch{CMD_SUFFIX}', f'zw{CMD_SUFFIX}']
        self.LeechCommand = [f'leech{CMD_SUFFIX}', f'l{CMD_SUFFIX}']
        self.UnzipLeechCommand = [
            f'unzipleech{CMD_SUFFIX}', f'uzl{CMD_SUFFIX}']
        self.ZipLeechCommand = [f'zipleech{CMD_SUFFIX}', f'zl{CMD_SUFFIX}']
        self.QbLeechCommand = [f'qbleech{CMD_SUFFIX}', f'qbl{CMD_SUFFIX}']
        self.QbUnzipLeechCommand = [
            f'qbunzipleech{CMD_SUFFIX}', f'qbuzl{CMD_SUFFIX}']
        self.QbZipLeechCommand = [
            f'qbzipleech{CMD_SUFFIX}', f'qbzl{CMD_SUFFIX}']
        self.YtdlLeechCommand = [
            f'ytdlleech{CMD_SUFFIX}', f'yl{CMD_SUFFIX}', f'leechwatch{CMD_SUFFIX}', f'lw{CMD_SUFFIX}']
        self.YtdlZipLeechCommand = [
            f'ytdlzipleech{CMD_SUFFIX}', f'yzl{CMD_SUFFIX}', f'zipwatch{CMD_SUFFIX}', f'zw{CMD_SUFFIX}']
        self.CloneCommand = [f'clone{CMD_SUFFIX}', f'cl{CMD_SUFFIX}']
        self.CountCommand = [f'count{CMD_SUFFIX}', f'co{CMD_SUFFIX}']
        self.DeleteCommand = [f'delete{CMD_SUFFIX}', f'del{CMD_SUFFIX}']
        self.CancelMirror = [f'cancel{CMD_SUFFIX}', f'c{CMD_SUFFIX}']
        self.CancelAllCommand = [f'cancelall{CMD_SUFFIX}', f'ca{CMD_SUFFIX}']
        self.ListCommand = [f'list{CMD_SUFFIX}', f'li{CMD_SUFFIX}']
        self.SearchCommand = [f'search{CMD_SUFFIX}', f'se{CMD_SUFFIX}']
        self.StatusCommand = [f'status{CMD_SUFFIX}', f'sta{CMD_SUFFIX}']
        self.UsersCommand = [f'users{CMD_SUFFIX}', f'us{CMD_SUFFIX}']
        self.AuthorizeCommand = [f'authorize{CMD_SUFFIX}', f'au{CMD_SUFFIX}']
        self.UnAuthorizeCommand = [
            f'unauthorize{CMD_SUFFIX}', f'ua{CMD_SUFFIX}']
        self.AddSudoCommand = [f'addsudo{CMD_SUFFIX}', f'as{CMD_SUFFIX}']
        self.RmSudoCommand = [f'rmsudo{CMD_SUFFIX}', f'rs{CMD_SUFFIX}']
        self.PingCommand = [f'ping{CMD_SUFFIX}', f'p{CMD_SUFFIX}']
        self.RestartCommand = [f'restart{CMD_SUFFIX}', f'r{CMD_SUFFIX}']
        self.StatsCommand = [f'stats{CMD_SUFFIX}', f'sts{CMD_SUFFIX}']
        self.HelpCommand = [f'help{CMD_SUFFIX}', f'h{CMD_SUFFIX}']
        self.LogCommand = [f'log{CMD_SUFFIX}', f'lo{CMD_SUFFIX}']
        self.ShellCommand = [f'shell{CMD_SUFFIX}', f'sh{CMD_SUFFIX}']
        self.EvalCommand = [f'eval{CMD_SUFFIX}', f'ev{CMD_SUFFIX}']
        self.ExecCommand = [f'exec{CMD_SUFFIX}', f'ex{CMD_SUFFIX}']
        self.ClearLocalsCommand = [f'clearlocals{CMD_SUFFIX}', f'clo{CMD_SUFFIX}']
        self.BotSetCommand = [f'bsetting{CMD_SUFFIX}', f'bset{CMD_SUFFIX}']
        self.UserSetCommand = [f'usetting{CMD_SUFFIX}', f'uset{CMD_SUFFIX}']
        self.BtSelectCommand = [f'btsel{CMD_SUFFIX}', f'bts{CMD_SUFFIX}']
        self.RssCommand = f'rss{CMD_SUFFIX}'


BotCommands = _BotCommands()
