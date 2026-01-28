import mysql.connector
import pandas as pd
from datetime import datetime

class RetailStoreDBLoader:
    def __init__(self, host, user, password, database):
        """Initialize database connection"""
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()
        print(f"Connected to database: {database}")
    
    def create_tables(self):
        """Create all tables with proper schema and relationships"""
        print("\n=== Creating Tables ===")
        
        # Drop tables if they exist (in reverse order due to foreign keys)
        drop_queries = [
            "DROP TABLE IF EXISTS SaleDetails;",
            "DROP TABLE IF EXISTS Sales;",
            "DROP TABLE IF EXISTS Products;",
            "DROP TABLE IF EXISTS Branches;",
            "DROP TABLE IF EXISTS Customers;"
        ]
        
        for query in drop_queries:
            self.cursor.execute(query)
        print("Dropped existing tables (if any)")
        
        # Create Customers table
        self.cursor.execute("""
            CREATE TABLE Customers (
                CustomerID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Gender VARCHAR(10),
                BirthDate DATE,
                Phone VARCHAR(20),
                Email VARCHAR(100),
                City VARCHAR(50),
                INDEX idx_city (City),
                INDEX idx_name (Name)
            );
        """)
        print("✓ Created Customers table")
        
        # Create Branches table
        self.cursor.execute("""
            CREATE TABLE Branches (
                BranchID INT AUTO_INCREMENT PRIMARY KEY,
                BranchName VARCHAR(100) NOT NULL,
                City VARCHAR(50),
                Address VARCHAR(200),
                INDEX idx_city (City)
            );
        """)
        print("✓ Created Branches table")
        
        # Create Products table
        self.cursor.execute("""
            CREATE TABLE Products (
                ProductID INT AUTO_INCREMENT PRIMARY KEY,
                ProductName VARCHAR(100) NOT NULL,
                Category VARCHAR(50),
                Price DECIMAL(10, 2),
                Supplier VARCHAR(100),
                INDEX idx_category (Category),
                INDEX idx_supplier (Supplier)
            );
        """)
        print("✓ Created Products table")
        
        # Create Sales table
        self.cursor.execute("""
            CREATE TABLE Sales (
                SaleID INT AUTO_INCREMENT PRIMARY KEY,
                CustomerID INT,
                BranchID INT,
                SaleDate DATE,
                TotalAmount DECIMAL(10, 2),
                FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE,
                FOREIGN KEY (BranchID) REFERENCES Branches(BranchID) ON DELETE CASCADE,
                INDEX idx_sale_date (SaleDate),
                INDEX idx_customer (CustomerID),
                INDEX idx_branch (BranchID)
            );
        """)
        print("✓ Created Sales table")
        
        # Create SaleDetails table
        self.cursor.execute("""
            CREATE TABLE SaleDetails (
                SaleDetailID INT AUTO_INCREMENT PRIMARY KEY,
                SaleID INT NOT NULL,
                ProductID INT NOT NULL,
                Quantity INT NOT NULL,
                UnitPrice DECIMAL(10, 2) NOT NULL,
                TotalPrice DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (SaleID) REFERENCES Sales(SaleID) ON DELETE CASCADE,
                FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE,
                INDEX idx_sale (SaleID),
                INDEX idx_product (ProductID)
            );
        """)
        print("✓ Created SaleDetails table")
        
        self.connection.commit()
        print("\nAll tables created successfully!")
    
    def load_customers(self, csv_file):
        """Load customers data from CSV"""
        print(f"\n=== Loading Customers from {csv_file} ===")

        try:
            df = pd.read_csv(csv_file)
            
            query = """
                INSERT INTO Customers (CustomerID, Name, Gender, BirthDate, Phone, Email, City)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            for index, row in df.iterrows():
                # Handle date conversion if needed
                birth_date = pd.to_datetime(row['BirthDate']).date() if pd.notna(row['BirthDate']) else None
                
                self.cursor.execute(query, (
                    row['CustomerID'],
                    row['Name'],
                    row['Gender'] if pd.notna(row['Gender']) else None,
                    birth_date,
                    row['Phone'] if pd.notna(row['Phone']) else None,
                    row['Email'] if pd.notna(row['Email']) else None,
                    row['City'] if pd.notna(row['City']) else None
                ))
            
            self.connection.commit()
            print(f"✓ Loaded {len(df)} customers")
            
        except Exception as e:
            print(f"✗ Error loading customers: {e}")
            self.connection.rollback()
    
    def load_branches(self, csv_file):
        """Load branches data from CSV"""
        print(f"\n=== Loading Branches from {csv_file} ===")
        try:
            df = pd.read_csv(csv_file)
            
            query = """
                INSERT INTO Branches (BranchID, BranchName, City, Address)
                VALUES (%s, %s, %s, %s)
            """
            
            for index, row in df.iterrows():
                self.cursor.execute(query, (
                    row['BranchID'],
                    row['BranchName'],
                    row['City'] if pd.notna(row['City']) else None,
                    row['Address'] if pd.notna(row['Address']) else None
                ))
            
            self.connection.commit()
            print(f"✓ Loaded {len(df)} branches")
            
        except Exception as e:
            print(f"✗ Error loading branches: {e}")
            self.connection.rollback()
    
    def load_products(self, csv_file):
        """Load products data from CSV"""
        print(f"\n=== Loading Products from {csv_file} ===")
        try:
            df = pd.read_csv(csv_file)
            
            query = """
                INSERT INTO Products (ProductID, ProductName, Category, Price, Supplier)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            for index, row in df.iterrows():
                self.cursor.execute(query, (
                    row['ProductID'],
                    row['ProductName'],
                    row['Category'] if pd.notna(row['Category']) else None,
                    row['Price'] if pd.notna(row['Price']) else None,
                    row['Supplier'] if pd.notna(row['Supplier']) else None
                ))
            
            self.connection.commit()
            print(f"✓ Loaded {len(df)} products")
            
        except Exception as e:
            print(f"✗ Error loading products: {e}")
            self.connection.rollback()
    
    def load_sales(self, csv_file):
        """Load sales data from CSV"""
        print(f"\n=== Loading Sales from {csv_file} ===")
        try:
            df = pd.read_csv(csv_file)
            
            query = """
                INSERT INTO Sales (SaleID, CustomerID, BranchID, SaleDate, TotalAmount)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            for index, row in df.iterrows():
                # Handle date conversion
                sale_date = pd.to_datetime(row['SaleDate']).date() if pd.notna(row['SaleDate']) else None
                
                self.cursor.execute(query, (
                    row['SaleID'],
                    row['CustomerID'],
                    row['BranchID'],
                    sale_date,
                    row['TotalAmount'] if pd.notna(row['TotalAmount']) else None
                ))
            
            self.connection.commit()
            print(f"✓ Loaded {len(df)} sales")
            
        except Exception as e:
            print(f"✗ Error loading sales: {e}")
            self.connection.rollback()
    
    def load_sale_details(self, csv_file):
        """Load sale details data from CSV"""
        print(f"\n=== Loading SaleDetails from {csv_file} ===")
        try:
            df = pd.read_csv(csv_file)
            
            query = """
                INSERT INTO SaleDetails (SaleID, ProductID, Quantity, UnitPrice, TotalPrice)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            for index, row in df.iterrows():
                self.cursor.execute(query, (
                    row['SaleID'],
                    row['ProductID'],
                    row['Quantity'],
                    row['UnitPrice'],
                    row['TotalPrice']
                ))
            
            self.connection.commit()
            print(f"✓ Loaded {len(df)} sale details")
            
        except Exception as e:
            print(f"✗ Error loading sale details: {e}")
            self.connection.rollback()
    
    def verify_data(self):
        """Verify loaded data by showing counts"""
        print("\n=== Data Verification ===")
        
        tables = ['Customers', 'Branches', 'Products', 'Sales', 'SaleDetails']
        
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            print(f"{table}: {count} records")
    
    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.connection.close()
        print("\n✓ Database connection closed")


def main():
    """Main function to run the database initialization and data loading"""
    
    # Database configuration
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'MySqlPassword_123',
        'database': 'retail_store'
    }
    
    # CSV file paths 
    CSV_FILES = {
        'customers': "Customers.csv",
        'branches': 'Branches.csv',
        'products': 'Products.csv',
        'sales': 'Sales_50000.csv',
        'sale_details': 'SaleDetails_200000.csv'
    }
    
    try:
        # Initialize loader
        loader = RetailStoreDBLoader(**DB_CONFIG)
        
        # Create tables
        loader.create_tables()
        
        # Load data from CSV files
        loader.load_customers(CSV_FILES['customers'])
        loader.load_branches(CSV_FILES['branches'])
        loader.load_products(CSV_FILES['products'])
        loader.load_sales(CSV_FILES['sales'])
        loader.load_sale_details(CSV_FILES['sale_details'])
        
        # Verify data
        loader.verify_data()
        
        # Close connection
        loader.close()
        
        print("\n" + "="*50)
        print("DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
        print("="*50)
        
    except mysql.connector.Error as e:
        print(f"\n✗ Database error: {e}")
    except FileNotFoundError as e:
        print(f"\n✗ CSV file not found: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()