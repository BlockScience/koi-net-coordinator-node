from .core import CoordinatorAssembler


node = CoordinatorAssembler.create()
node.server.run()