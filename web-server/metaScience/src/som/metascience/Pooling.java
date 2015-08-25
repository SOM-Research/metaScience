package som.metascience;

import java.sql.Connection;
import java.sql.SQLException;

import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.NamingException;
import org.apache.tomcat.jdbc.pool.DataSource;

public class Pooling {
	private static Pooling instance = null;
	private static DataSource dataSource;
	
	public static Pooling getInstance() {
		if (instance == null) {
			instance = new Pooling();
			initContext();
		}
		return instance;
	}
	
	private static void initContext() {
		if (dataSource == null)
			try {				
				InitialContext initContext = new InitialContext();
				Context envContext = (Context) initContext.lookup("java:comp/env");
				dataSource = (DataSource) envContext.lookup("jdbc/dbCon");
			} catch (NamingException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
	}
	
	public Connection getConnection() {
		Connection connection = null;
		try {
            if(dataSource == null) initContext();
            connection = dataSource.getConnection();
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return connection;
	}
}
