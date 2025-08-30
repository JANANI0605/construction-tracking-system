# construction-tracking-system

A comprehensive web application for managing construction projects, built with Flask and Oracle Database. This system enables contractors to manage multiple projects while providing customers with real-time visibility into their project status and payments.

## Overview

The Construction Tracking System streamlines project management for construction businesses by providing separate interfaces for contractors and customers. Contractors can manage projects, materials, and payments, while customers can track progress and view project details.

## Key Features

**Contractor Management**
- Project creation and management
- Material inventory tracking
- Payment processing and history
- Customer assignment and communication
- Project status updates

**Customer Portal**
- Real-time project status viewing
- Payment history and tracking
- Contractor contact information
- Profile management

## Database Structure

The application uses Oracle Database with five core tables:

- **customer** - Customer information and project assignments
- **contractor** - Contractor profiles and specializations  
- **project** - Project details, timeline, and costs
- **material** - Material inventory and project allocation
- **payment** - Payment records and transaction history

## Getting Started

### Prerequisites

- Python 3.7+
- Oracle Database XE

### Installation

1. Clone the repository:
git clone https://github.com/JANANI0605/construction-tracking-system.git
cd construction-tracking-system

2. Create and activate virtual environment:
python -m venv venv
**Windows:**
venv\Scripts\activate

3. Install dependencies:
   Flask==2.3.3
   oracledb==1.4.2
   
4. Configure Oracle connection:
   - Ensure your Oracle database is running
   - Update database connection settings in your application

5. Initialize the database:
   - Create the required tables using the provided schema
   - Optionally load sample data for testing

6. Start the application:
python app.py

The application will be available at `http://localhost:5000`

## Technology Stack
- **Backend Framework**: Flask
- **Database**: Oracle Database XE
- **Frontend**: HTML, CSS
- **Database Connectivity**: Python Oracle driver (oracledb)

## Project Structure
The application follows a standard Flask structure with separate modules for different functionality areas. Database operations are handled through Python's Oracle database driver with proper connection management.

## Contributing
This project was developed as part of a database management system course. Feel free to fork and adapt for your own construction management needs.

## Author
Janani Saravanan 
[GitHub Profile](https://github.com/JANANI0605)
