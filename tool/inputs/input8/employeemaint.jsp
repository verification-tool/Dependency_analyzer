<%@ include file="Common.jsp" %><%!
//
//   Filename: EmployeeMaint.jsp
//   Generated with CodeCharge  v.1.2.0
//   JSP.ccp build 05/21/2001
//

static final String sFileName = "EmployeeMaint.jsp";
              
static final String PageBODY = "bgcolor=\"#F3F2E6\" text=\"#000000\" link=\"#800000\" vlink=\"#000080\" alink=\"#0000FF\"";
static final String FormTABLE = "border=\"1\" cellspacing=\"0\" cellpadding=\"2\" bordercolorlight=\"#000000\" bordercolordark=\"#FFFFFF\"";
static final String FormHeaderTD = "align=\"center\" bgcolor=\"#669999\"";
static final String FormHeaderFONT = "style=\"font-size: 12pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica; font-weight: bold\"";
static final String FieldCaptionTD = "bgcolor=\"#B3B300\"";
static final String FieldCaptionFONT = "style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\"";
static final String DataTD = "bgcolor=\"#F0F0F0\"";
static final String DataFONT = "style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\"";
static final String ColumnFONT = "style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica; font-weight: bold\"";
static final String ColumnTD = "bgcolor=\"#B3B300\"";
%><%

boolean bDebug = false;

String sAction = getParam( request, "FormAction");
String sForm = getParam( request, "FormName");
String sEmployeeErr = "";

java.sql.Connection conn = null;
java.sql.Statement stat = null;
String sErr = loadDriver();
conn = cn();
stat = conn.createStatement();
if ( ! sErr.equals("") ) {
 try {
   out.println(sErr);
 }
 catch (Exception e) {}
}
if ( sForm.equals("Employee") ) {
  sEmployeeErr = EmployeeAction(request, response, session, out, sAction, sForm, conn, stat);
  if ( "sendRedirect".equals(sEmployeeErr)) return;
}

%>            
<html>
<head>
<title>Employee Maintenance</title>
<meta name="GENERATOR" content="YesSoftware CodeCharge v.1.2.0 / JSP.ccp build 05/21/2001"/>
<meta http-equiv="pragma" content="no-cache"/>
<meta http-equiv="expires" content="0"/>
<meta http-equiv="cache-control" content="no-cache"/>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
</head>
<body bgcolor="#F3F2E6" text="#000000" link="#800000" vlink="#000080" alink="#0000FF">
<jsp:include page="Header.jsp" flush="true"/>
 <table>
  <tr>
   
   <td valign="top">
<% Employee_Show(request, response, session, out, sEmployeeErr, sForm, sAction, conn, stat); %>
    <SCRIPT Language="JavaScript">
if (document.forms["Employee"])
document.Employee.onsubmit=delconf;
function delconf() {
if (document.Employee.FormAction.value == 'delete')
  return confirm('Delete record?');
}
</SCRIPT>
   </td>
  </tr>
 </table>


<center><font face="Arial"><small>This dynamic site was generated with <a href="http://www.codecharge.com">CodeCharge</a></small></font></center>
</body>
</html>
<%%>
<%
if ( stat != null ) stat.close();
if ( conn != null ) conn.close();
%>
<%!


  String EmployeeAction(javax.servlet.http.HttpServletRequest request, javax.servlet.http.HttpServletResponse response, javax.servlet.http.HttpSession session, javax.servlet.jsp.JspWriter out, String sAction, String sForm, java.sql.Connection conn, java.sql.Statement stat) throws java.io.IOException {
  
    String sEmployeeErr ="";
    try {

      if (sAction.equals("")) return "";

      String sSQL="";
      String transitParams = "";
      String primaryKeyParams = "";
      String sQueryString = "";
      String sPage = "";
      String sParams = "";
      String sActionFileName = "EmployeeList.jsp";
      String sWhere = " ";
      boolean bErr = false;
      long iCount = 0;

  
      String pPKemployee_id = "";

      final int iinsertAction = 1;
      final int iupdateAction = 2;
      final int ideleteAction = 3;
      int iAction = 0;

      if ( sAction.equalsIgnoreCase("insert") ) { iAction = iinsertAction; }
      if ( sAction.equalsIgnoreCase("update") ) { iAction = iupdateAction; }
      if ( sAction.equalsIgnoreCase("delete") ) { iAction = ideleteAction; }

      

     
      String fldsecurity_level="";
      String fldperformance_rate="";
      String fldwork_experience="";
      String fldemp_id="";

      // Load all form fields into variables
    
      fldperformance_rate = getParam(request, "performance_rate");
      fldsecurity_level = getParam(request, "security_level");
      fldemp_name = getParam(request, "emp_id");
      fldwork_experience = getParam(request, "work_experience");
      // Validate fields
      if ( iAction == iinsertAction || iAction == iupdateAction ) {
        if ( isEmpty(fldwork_experience) ) {
          sEmployeeErr = sEmployeeErr + "The value in field work_experience is required.<br>";
        }
        if ( isEmpty(fldperformance_rate) ) {
          sEmployeeErr = sEmployeeErr + "The value in field performance_rate is required.<br>";
        }
        if ( isEmpty(fldsecurity_level) ) {
          sEmployeeErr = sEmployeeErr + "The value in field Security Level is required.<br>";
        }
        if ( isEmpty(fldemp_id) ) {
          sEmployeeErr = sEmployeeErr + "The value in field id is required.<br>";
        }
        if ( ! isNumber(fldsecurity_level)) {
          sEmployeeErr = sEmployeeErr + "The value in field Security Level is incorrect.<br>";
        }
        if (sEmployeeErr.length() > 0 ) {
          return (sEmployeeErr);
        }
      }


      sSQL = "";
      // Create SQL statement

      switch (iAction) {
  
        case iinsertAction :
          
            sSQL = "insert into employees (" + 
                "emp_id," +
                "security_level," +
                "performance_rate," +
                "work_experience)" +

                " values (" + 
                "emp_id," +
                "security_level," +
                "performance_rate," +
                "work_experience)";
          break;
  
      
  
       }

      if ( sEmployeeErr.length() > 0 ) return sEmployeeErr;
      try {
        // Execute SQL statement
        stat.executeUpdate(sSQL);
        stat.executeUpdate("UPDATE employees SET security_level = 3 WHERE work_experience >= 5");
        stat.executeUpdate("update employees set security_level = security_level + 1 where performance_rate + work_experience >=90 ");
       
        stat.executeUpdate("update employees set security_level = security_level - 1 where performance_rate + work_experience <=40 ");
      
        stat.executeUpdate("delete from employees where performance_rate <= 10");

         java.sql.ResultSet rs = null;
       
        rs = openrs( stat, "SELECT * From employees ");

        stat.executeUpdate("UPDATE employees SET work_experience = work_experience + security_level WHERE security_level > 2");

        rs = openrs( stat, "SELECT emp_id FROM employees");

        stat.executeUpdate("UPDATE employees SET work_experience = work_experience + 1 WHERE security_level = 3")


         File file = new File("/users/mkyong/filename.txt");

			// if file doesnt exists, then create it
			if (!file.exists()) {
				file.createNewFile();
			}

			FileWriter fw = new FileWriter(file.getAbsoluteFile());
			BufferedWriter bw = new BufferedWriter(fw);
			



       while (rs.next()){
        String[] aFields = getFieldsName( rs );
        getRecordToHash( rs, rsHash, aFields );
        
            
        fldemp_id = (String) rsHash.get("emp_id");
        bw.write(fldemp_id);
       
        fldsecurity_level = (String) rsHash.get("security_level");
        bw.write(fldsecurity_level);  
        fldwork_experience = (String) rsHash.get("work_experience");
        bw.write(fldwork_experience);
        fldperformance_rate = (String) rsHash.get("performance_rate");
        bw.write(fldperformance_rate);
      
      
       }
       rs.close();
       
  
      }
      catch(java.sql.SQLException e) {
        sEmployeeErr = e.toString(); return (sEmployeeErr);
      }
  
      try {
        if ( stat != null ) stat.close();
        if ( conn != null ) conn.close();
      }
      catch ( java.sql.SQLException ignore ) {}
      response.sendRedirect (sActionFileName);

      return "sendRedirect";
    }
    catch (Exception e) {out.println(e.toString()); }
    return (sEmployeeErr);
  }

  


  void Employee_Show(javax.servlet.http.HttpServletRequest request, javax.servlet.http.HttpServletResponse response, javax.servlet.http.HttpSession session, javax.servlet.jsp.JspWriter out, String sEmployeeErr, String sForm, String sAction, java.sql.Connection conn, java.sql.Statement stat) throws java.io.IOException {
    try {

      String sSQL="";
      String sQueryString = "";
      String sPage = "";
      String sWhere = "";
      String transitParams = "";
      String transitParamsHidden = "";
      String requiredParams = "";
      String primaryKeyParams ="";
      java.util.Hashtable rsHash = new java.util.Hashtable();
      
      String pemployee_id = "";

      String fldemp_id="";
      String fldwork_experience="";
      String fldperformance_rate="";
      String fldsecurity_level="";
     


      boolean bPK = true;

      if ( "".equals(sEmployeeErr)) {
        // Load primary key and form parameters
        pemp_id = getParam( request, "emp_id");
      }
      else {
        // Load primary key, form parameters and form fields
        fldemp_id = (String) rsHash.get("emp_id");
          fldwork_experience = (String) rsHash.get("work_experience");
          fldperformance_rate = (String) rsHash.get("performance_rate");
          fldsecurity_level = (String) rsHash.get("security_level");
         
      }

      
      if ( isEmpty(pemployee_id)) { bPK = false; }
      
      //sWhere += "employee_id=" + toSQL(pemployee_id, adNumber);
      primaryKeyParams += "<input type=\"hidden\" name=\"PK_employee_id\" value=\""+pemployee_id+"\"/>";

     // sSQL = "select * from employees where " + sWhere;


      out.println("    <table border=\"1\" cellspacing=\"0\" cellpadding=\"2\" bordercolorlight=\"#000000\" bordercolordark=\"#FFFFFF\">");
      out.println("     <tr>\n      <td align=\"center\" bgcolor=\"#669999\" colspan=\"2\"><font style=\"font-size: 12pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica; font-weight: bold\">Add/Edit Employee</font></td>\n     </tr>");
      if ( ! sEmployeeErr.equals("")) {
        out.println("     <tr>\n      <td bgcolor=\"#F0F0F0\" colspan=\"2\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">"+sEmployeeErr+"</font></td>\n     </tr>");
      }
      sEmployeeErr="";
      out.println("     <form method=\"get\" action=\""+sFileName+"\" name=\"Employee\">");

      java.sql.ResultSet rs = null;

      if ( bPK &&  ! (sAction.equals("insert") && "Employee".equals(sForm))) {

        // Open recordset
        
        }

        if (sAction.equals("") || ! "Employee".equals(sForm)) {
      
          fldemp_id = (String) rsHash.get("emp_id");
          fldwork_experience = (String) rsHash.get("work_experience");
          fldperformance_rate = (String) rsHash.get("performance_rate");
          fldsecurity_level = (String) rsHash.get("security_level");
         
        }
        
      }
      else {
      }
      


      // Show form field
      
      out.print("     <tr>\n      <td bgcolor=\"#B3B300\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Login</font></td><td bgcolor=\"#F0F0F0\">"); out.print("<input type=\"text\"  name=\"login\" maxlength=\"15\" value=\""+toHTML(fldlogin)+"\" size=\"15\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#B3B300\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Password</font></td><td bgcolor=\"#F0F0F0\">"); out.print("<input type=\"password\"  name=\"pass\" maxlength=\"15\" value=\""+toHTML(fldpass)+"\" size=\"15\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#B3B300\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Security Level</font></td><td bgcolor=\"#F0F0F0\">"); 
      out.print("<select name=\"security_level\">"+getOptionsLOV("1;Developer;3;Administrator",false,true,fldsecurity_level)+"</select>");
      
      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#B3B300\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Name</font></td><td bgcolor=\"#F0F0F0\">"); out.print("<input type=\"text\"  name=\"employee_name\" maxlength=\"30\" value=\""+toHTML(fldemployee_name)+"\" size=\"30\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#B3B300\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Email</font></td><td bgcolor=\"#F0F0F0\">"); out.print("<input type=\"text\"  name=\"email\" maxlength=\"30\" value=\""+toHTML(fldemail)+"\" size=\"30\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td colspan=\"2\" align=\"right\">");
      

      if ( bPK && ! (sAction.equals("insert") && "Employee".equals(sForm))) {
        out.print("<input type=\"submit\" value=\"Update\" onclick=\"document.Employee.FormAction.value = 'update';\">");out.print("<input type=\"submit\" value=\"Delete\" onclick=\"document.Employee.FormAction.value = 'delete';\">");
        out.print("<input type=\"hidden\" name=\"FormName\" value=\"Employee\"><input type=\"hidden\" value=\"update\" name=\"FormAction\">");
      }
      
      else {
        out.print("<input type=\"submit\" value=\"Add\" onclick=\"document.Employee.FormAction.value = 'insert';\">");
        out.print("<input type=\"hidden\" name=\"FormName\" value=\"Employee\"><input type=\"hidden\" value=\"insert\" name=\"FormAction\">");
      }out.print("<input type=\"hidden\" name=\"emp_id\" value=\""+toHTML(fldemp_id)+"\">");
      out.print(transitParamsHidden+requiredParams+primaryKeyParams);
      out.println("</td>\n     </tr>\n     </form>\n    </table>");
      



    }
    catch (Exception e) { out.println(e.toString()); }
  } %>