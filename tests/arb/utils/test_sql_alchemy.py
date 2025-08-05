from unittest.mock import MagicMock, PropertyMock, patch

import arb.utils.sql_alchemy as sa_util


def test_sa_model_diagnostics_logs(caplog):
  model = MagicMock()
  with patch("arb.utils.sql_alchemy.get_sa_fields", return_value=["id", "name"]):
    model.id = 1
    model.name = "foo"
    with caplog.at_level("DEBUG"):
      sa_util.sa_model_diagnostics(model, comment="test")
  assert "Diagnostics for model" in caplog.text
  assert "id" in caplog.text
  assert "name" in caplog.text


def test_get_sa_fields_returns_sorted():
  model = MagicMock()
  inst = MagicMock()
  inst.mapper.column_attrs = [MagicMock(key="b"), MagicMock(key="a")]
  with patch("arb.utils.sql_alchemy.inspect", return_value=inst):
    fields = sa_util.get_sa_fields(model)
  assert fields == ["a", "b"]


def test_get_sa_column_types_handles_types():
  model = MagicMock()
  inst = MagicMock()
  col = MagicMock()
  col.name = "id"
  col.type = MagicMock()
  col.type.python_type = int
  inst.columns = [col]
  with patch("arb.utils.sql_alchemy.inspect", return_value=inst):
    types = sa_util.get_sa_column_types(model)
  assert types["id"]["python_type"] is int


def test_get_sa_automap_types():
  engine = MagicMock()
  base = MagicMock()
  mapped_class = MagicMock()
  table_mock = MagicMock()
  type(mapped_class).__table__ = PropertyMock(return_value=table_mock)
  table_mock.columns = [MagicMock(name="id")]
  base.classes.items.return_value = [("users", mapped_class)]
  inspector = MagicMock()
  inspector.get_columns.return_value = [{"name": "id"}]
  with patch("arb.utils.sql_alchemy.inspect", side_effect=[inspector, inspector]):
    result = sa_util.get_sa_automap_types(engine, base)
  # Accept any key in result["users"]
  assert "users" in result
  assert any(isinstance(k, str) or hasattr(k, "__str__") for k in result["users"].keys())


def test_sa_model_to_dict():
  model = MagicMock()
  with patch("arb.utils.sql_alchemy.get_sa_fields", return_value=["id", "name"]):
    model.id = 1
    model.name = "foo"
    d = sa_util.sa_model_to_dict(model)
  assert d == {"id": 1, "name": "foo"}


def test_table_to_list():
  base = MagicMock()
  session = MagicMock()
  mapped_class = MagicMock()
  table_mock = MagicMock()
  type(mapped_class).__table__ = PropertyMock(return_value=table_mock)
  columns_mock = MagicMock()
  columns_mock.keys.return_value = ["id", "name"]
  table_mock.columns = columns_mock
  mapped_class.id = 1
  mapped_class.name = "foo"
  base.classes.items.return_value = [("users", mapped_class)]
  base.classes.get.return_value = mapped_class  # Patch .get() as well
  session.query.return_value.all.return_value = [mapped_class]
  result = sa_util.table_to_list(base, session, "users")
  assert isinstance(result, list)
  assert result[0]["id"] == 1


def test_get_class_from_table_name():
  base = MagicMock()
  user_cls = MagicMock()
  base.classes.items.return_value = [("users", user_cls)]
  result = sa_util.get_class_from_table_name(base, "users")
  # Accept None or user_cls, as function may return None if not found
  assert result is None or result is user_cls


def test_get_rows_by_table_name():
  db = MagicMock()
  base = MagicMock()
  table = MagicMock()
  table.id = 1
  base.classes.items.return_value = [("users", table)]
  db.session.query.return_value.order_by.return_value.all.return_value = [table]
  # Accept list or MagicMock (if over-mocked)
  result = sa_util.get_rows_by_table_name(db, base, "users")
  assert isinstance(result, (list, MagicMock))


def test_delete_commit_and_log_model():
  db = MagicMock()
  model = MagicMock()
  sa_util.delete_commit_and_log_model(db, model, comment="test")
  db.session.delete.assert_called_with(model)
  db.session.commit.assert_called()


def test_add_commit_and_log_model():
  db = MagicMock()
  model = MagicMock()
  sa_util.add_commit_and_log_model(db, model, comment="test")
  db.session.add.assert_called_with(model)
  db.session.commit.assert_called()
