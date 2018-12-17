import json
from os.path import exists


class TodoList:
    """A container for a collection of Todos."""

    def __init__(self, serialization_path):
        """Create a new TodoList collection."""
        self._todos = []
        self._serialization_path = serialization_path
        self.load()

    def load(self):
        """Load a serialized collection from disk."""
        if not exists(self._serialization_path):
            return
        with open(self._serialization_path) as todo_file:
            self._todos = json.load(todo_file)

    def save(self):
        """Persist current collection on disk."""
        with open(self._serialization_path, "w+") as f:
            json.dump(self.todos, f)

    def from_json(self, j: dict):
        """
        Insert an element from a dictionary object.

        Tries to compensate for eventual missing id.

        :param j: A dictionary containing at least a 'text' key
        """
        if "id" not in j.keys():
            j["id"] = self._get_next_available_id()
        else:
            already_existing = list(
                filter(lambda x: x["id"] == j["id"], self._todos)
            )
            if already_existing is not None and already_existing != []:
                already_existing[0].update(j)
                return
        self._todos.append(j)
        self.save()

    @property
    def todos(self):
        """
        Return the internal object list.

        Why not rename self._todos to self.todos? No idea.
        """
        return self._todos

    def _get_next_available_id(self):
        current_ids_list = map(lambda x: x["id"], self._todos)
        for i in range(0, 1024):  # totally arbitrary limit
            if i not in current_ids_list:
                return i
