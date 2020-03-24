from alembic import util
from alembic.script import ScriptDirectory
from graphviz import Digraph


RELEASE_REVISION_TAG = '[RELEASE-MERGE]'


def is_release_revision(revision):
    rval = revision.doc.startswith(RELEASE_REVISION_TAG)
    return rval


def get_node_name(revision):
    if is_release_revision(revision):
        return revision.doc[len(RELEASE_REVISION_TAG) + 1:]
    else:
        return revision.revision


def get_revisions(config, rev_range=None):
    script = ScriptDirectory.from_config(config)

    if rev_range is not None:
        if ":" not in rev_range:
            raise util.CommandError("History range requires [start]:[end], [start]:, or :[end]")
        base, head = rev_range.strip().split(":")
    else:
        base = head = None

    return script.walk_revisions(
        base=base or "base",
        head=head or "heads",
    )


def generate_revision_graph(revisions, fmt, config):
    script = ScriptDirectory.from_config(config)
    dot = Digraph(format=fmt)
    for revision in revisions:
        color = 'turquoise' if is_release_revision(revision) else None
        node_name = get_node_name(revision)
        dot.node(node_name, color=color)

        if revision.down_revision is None:
            dot.edge('base', get_node_name(revision))
            continue

        if isinstance(revision.down_revision, str):
            down_revision = script.get_revision(revision.down_revision)
            down_node_name = get_node_name(down_revision)
            dot.edge(down_node_name, get_node_name(revision))
            continue

        for down_revision in revision.down_revision:
            down_revision = script.get_revision(down_revision)
            down_node_name = get_node_name(down_revision)
            dot.edge(down_node_name, node_name)

    return dot
