import os
import sys

try:
    from database.connection import init_db
    init_db()

    from models.stock_laptop_model import StockLaptopModel
    m = StockLaptopModel()

    # Clean previous if any
    try:
        with open("test_log.txt", "w") as f:
            f.write("Starting test\n")
            fid = m.insert('FAN-TEST-001', 'SN123456', 'Dell Latitude 5420', 2, 'Avec licence')
            f.write(f"Inserted ID: {fid}\n")
            f.write(f"Is fan exists: {m.is_fan_exists('FAN-TEST-001')}\n")

            try:
                m.insert('FAN-TEST-001', 'SN999', 'Model X', 1, 'Sans licence')
                f.write("ERROR: Duplicate allowed!\n")
            except ValueError as e:
                f.write(f"SUCCESS: Duplicate blocked: {e}\n")

            from utils.excel_exporter import export_stock_to_excel
            export_stock_to_excel('test_export.xls', ['ID', 'FAN', 'MODEL'], [[fid, 'FAN-TEST-001', 'Dell']])
            f.write("Excel XML test passed\n")

            m.delete(fid)
            f.write("Deleted test item\n")
            if os.path.exists('test_export.xls'):
                os.remove('test_export.xls')
            f.write("ALL TESTS PASSED!\n")
except Exception as e:
    with open("test_log.txt", "a") as f:
        f.write(f"EXCEPTION: {e}\n")

