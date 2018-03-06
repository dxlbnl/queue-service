import trafaret as T


TRAFARET = T.Dict({
    T.Key('postgres'):
        T.Dict({
            'database': T.String(),
            'user': T.String(),
            # 'password': T.Any(T.String(), T.Null()),
            'host': T.String(),
            # 'port': T.Int(),
            T.Key('minsize', optional=True):  T.Int(),
            T.Key('maxsize', optional=True): T.Int(),
        }),
    T.Key('host', optional=True): T.IP,
    T.Key('port', optional=True): T.Int(),
    T.Key('path', optional=True): T.String(),
})
