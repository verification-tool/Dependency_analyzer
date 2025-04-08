<%@ include file="Common.jsp" %><%!
//
//   Filename: EmpsRecord.jsp
//   Generated with CodeCharge  v.1.2.0
//   JSP.ccp build 05/21/01
//

static final String sFileName = "EmpsRecord.jsp";
              
static final String PageBODY = "text=\"#000000\" link=\"#000080\" vlink=\"#000080\" alink=\"#000080\"";
static final String FormTABLE = "border=\"0\" cellspacing=\"2\" cellpadding=\"0\"";
static final String FormHeaderTD = "align=\"center\" bgcolor=\"#FFBB55\"";
static final String FormHeaderFONT = "style=\"font-size: 12pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica; font-weight: bold\"";
static final String FieldCaptionTD = "bgcolor=\"#FFDD00\"";
static final String FieldCaptionFONT = "style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\"";
static final String DataTD = "";
static final String DataFONT = "style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\"";
static final String ColumnFONT = "style=\"font-size: 10pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica; font-weight: bold\"";
static final String ColumnTD = "bgcolor=\"#000000\"";
%><%

String cSec = checkSecurity(3, session, response, request);
if ("sendRedirect".equals(cSec) ) return;
                
boolean bDebug = false;

String sAction = getParam( request, "FormAction");
String sForm = getParam( request, "FormName");
String sempsErr = "";

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
if ( sForm.equals("emps") ) {
  sempsErr = empsAction(request, response, session, out, sAction, sForm, conn, stat);
  if ( "sendRedirect".equals(sempsErr)) return;
}

%>            
<html>
<head>
<title>Employee Directory</title>
<meta name="GENERATOR" content="YesSoftware CodeCharge v.1.2.0 / JSP.ccp build 05/21/01"/>
<meta http-equiv="pragma" content="no-cache"/>
<meta http-equiv="expires" content="0"/>
<meta http-equiv="cache-control" content="no-cache"/>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
</head>
<body text="#000000" link="#000080" vlink="#000080" alink="#000080">
<jsp:include page="Header.jsp" flush="true"/>
 <table>
  <tr>
   
   <td valign="top">
<% emps_Show(request, response, session, out, sempsErr, sForm, sAction, conn, stat); %>
    <SCRIPT Language="JavaScript">
if (document.forms["emps"])
  document.emps.onsubmit=delconf;
function delconf() {
if (document.emps.FormAction.value == 'delete')
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


  String empsAction(javax.servlet.http.HttpServletRequest request, javax.servlet.http.HttpServletResponse response, javax.servlet.http.HttpSession session, javax.servlet.jsp.JspWriter out, String sAction, String sForm, java.sql.Connection conn, java.sql.Statement stat) throws java.io.IOException {
  
    String sempsErr ="";
    try {

      if (sAction.equals("")) return "";

      String sSQL="";
      String transitParams = "";
      String primaryKeyParams = "";
      String sQueryString = "";
      String sPage = "";
      String sParams = "";
      String sActionFileName = "EmpsGrid.jsp";
      String sWhere = " ";
      boolean bErr = false;
      long iCount = 0;

  
      //String pPKemp_id = "";
      if (sAction.equalsIgnoreCase("cancel") ) {
        try {
          if ( stat != null ) stat.close();
          if ( conn != null ) conn.close();
        }
        catch ( java.sql.SQLException ignore ) {}
        response.sendRedirect (sActionFileName);
        return "sendRedirect";
      }

      final int iinsertAction = 1;
      final int iupdateAction = 2;
      final int ideleteAction = 3;
      int iAction = 0;

      if ( sAction.equalsIgnoreCase("insert") ) { iAction = iinsertAction; }
      if ( sAction.equalsIgnoreCase("update") ) { iAction = iupdateAction; }
      if ( sAction.equalsIgnoreCase("delete") ) { iAction = ideleteAction; }

      


      String fldage="";
      String fldcom="";
      String fldda="";
      String fldhra="";
      String fldbasic="";
      String flddepid="";
      
      String fldempid="";

      // Load all form fields into variables
    
      fldage = getParam(request, "age");
      fldcom = getParam(request, "com");
      fldda = getParam(request, "da");
      fldhra = getParam(request, "hra");
      fldbasic = getParam(request, "basic");
      flddep_id = getParam(request, "depid");
     
      // Validate fields
      if ( iAction == iinsertAction || iAction == iupdateAction ) {
        if ( isEmpty(fldage) ) {
          sempsErr = sempsErr + "The value in field Name is required.<br>";
        }
        if ( isEmpty(fldcom) ) {
          sempsErr = sempsErr + "The value in field Title is required.<br>";
        }
        if ( isEmpty(fldda) ) {
          sempsErr = sempsErr + "The value in field Login is required.<br>";
        }
        if ( isEmpty(fldhra) ) {
          sempsErr = sempsErr + "The value in field Password is required.<br>";
        }
        if ( isEmpty(fldbasic) ) {
          sempsErr = sempsErr + "The value in field Level is required.<br>";
        }
        if ( isEmpty(flddepid) ) {
          sempsErr = sempsErr + "The value in field Department is required.<br>";
        }
        
        if ( ! isEmpty(fldempid)) {
          iCount = 0;
          if ( iAction == iinsertAction ) {
            iCount = dCountRec(stat, "emps", "empid=" + sWhere);
          }
          else {
            if ( iAction == iupdateAction ) {
              iCount = dCountRec( stat, "emps", "empid=" + sWhere);
            }
          }
          if (iCount > 0) {
            sempsErr = sempsErr + "The value in field Login is already in database.<br>";
          }
        }
        if (sempsErr.length() > 0 ) {
          return (sempsErr);
        }
      }


      sSQL = "";
      

      if ( sempsErr.length() > 0 ) return sempsErr;
      try {
        // Execute SQL statement
        //stat.executeUpdate(sSQL);

        stat.executeUpdate("update emps set com = com + com * 0.1 where depid >=4");

        stat.executeUpdate("update emps set com = com + com * 0.05 where depid <=3");

        stat.executeUpdate("select depid emps where depid <=3");
        stat.executeUpdate("delete from emps where age >= 61");
       
        


       java.sql.ResultSet rs1 = null;

      
     

        rs1 = openrs( stat, "select age from emps where age <= 60");




         File file = new File("/users/mkyong/filename.txt");

			// if file doesnt exists, then create it
			if (!file.exists()) {
				file.createNewFile();
			}

			FileWriter fw = new FileWriter(file.getAbsoluteFile());
			BufferedWriter bw = new BufferedWriter(fw);
			



        while(rs1.next()){
        String[] aFields = getFieldsName( rs1 );
        getRecordToHash( rs1, rsHash, aFields );
        
        fldempid = (String) rsHash.get("empid");
        bw.write(fldempid);
        fldage = (String) rsHash.get("age");
        bw.write(fldage);
        fldcom = (String) rsHash.get("com");
        bw.write(fldcom);    
        fldda = (String) rsHash.get("da");
        bw.write(fldda);
        fldhra = (String) rsHash.get("hra");
        bw.write(fldhra);
        fldbasic = (String) rsHash.get("basic");
        bw.write(fldbasic);
        flddepid = (String) rsHash.get("depid");
        bw.write(flddepid);
          
        }
        rs1.close();

            

        stat.executeUpdate("update emps set basic = basic + .03 * basic where basic + da + hra >= 20000");
 
        stat.executeUpdate("update emps set basic = basic + 1000 where basic + da + hra >= 0");

     
        




       java.sql.ResultSet rs2 = null;

      
       

        rs2 = openrs( stat, "select * from emps where basic + da + hra <= 25000");




         File file = new File("/users/mkyong/filename.txt");

			// if file doesnt exists, then create it
			if (!file.exists()) {
				file.createNewFile();
			}

			FileWriter fw = new FileWriter(file.getAbsoluteFile());
			BufferedWriter bw = new BufferedWriter(fw);
			



        while(rs2.next()){
        String[] aFields = getFieldsName( rs2 );
        getRecordToHash( rs2, rsHash, aFields );
       
        fldempid = (String) rsHash.get("empid");
        bw.write(fldempid);
        fldage = (String) rsHash.get("age");
        bw.write(fldage);
        fldcom = (String) rsHash.get("com");
        bw.write(fldcom);    
        fldda = (String) rsHash.get("da");
        bw.write(fldda);
        fldhra = (String) rsHash.get("hra");
        bw.write(fldhra);
        fldbasic = (String) rsHash.get("basic");
        bw.write(fldbasic);
        flddepid = (String) rsHash.get("depid");
        bw.write(flddepid);

      }
     rs2.close();


      }
      catch(java.sql.SQLException e) {
        sempsErr = e.toString(); return (sempsErr);
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
    return (sempsErr);
  }

  


  void emps_Show(javax.servlet.http.HttpServletRequest request, javax.servlet.http.HttpServletResponse response, javax.servlet.http.HttpSession session, javax.servlet.jsp.JspWriter out, String sempsErr, String sForm, String sAction, java.sql.Connection conn, java.sql.Statement stat) throws java.io.IOException {
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
      
      //String pemp_id = "";

      String fldempid="";
      String fldage="";
      String fldcom="";
      String fldda="";
      String fldhra="";
      String fldbasic="";
      String flddepid="";
      
      boolean bPK = true;

      if ( "".equals(sempsErr)) {
        // Load primary key and form parameters
        fldempid = getParam( request, "empid");
        //pemp_id = getParam( request, "emp_id");
      }
      else {
        // Load primary key, form parameters and form fields
        fldempid = getParam( request, "empid");
        fldage = getParam( request, "age");
        fldcom = getParam( request, "com");
        fldda = getParam( request, "da");
        fldhra = getParam( request, "hra");
        fldbasic = getParam( request, "basic");
        flddepid = getParam( request, "depid");
        fldaddress = getParam( request, "address");
      }

      
      if ( isEmpty(pemp_id)) { bPK = false; }
      
      sWhere = " fldempid";
      //primaryKeyParams += "<input type=\"hidden\" name=\"PK_emp_id\" value=\""+pemp_id+"\"/>";

      sSQL = "select * from emps where "+"empid=" + sWhere;


      out.println("    <table border=\"0\" cellspacing=\"2\" cellpadding=\"0\">");
      out.println("     <tr>\n      <td align=\"center\" bgcolor=\"#FFBB55\" colspan=\"2\"><font style=\"font-size: 12pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica; font-weight: bold\">emps</font></td>\n     </tr>");
      if ( ! sempsErr.equals("")) {
        out.println("     <tr>\n      <td  colspan=\"2\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">"+sempsErr+"</font></td>\n     </tr>");
      }
      sempsErr="";
      out.println("     <form method=\"get\" action=\""+sFileName+"\" name=\"emps\">");

      java.sql.ResultSet rs = null;

      if ( bPK &&  ! (sAction.equals("insert") && "emps".equals(sForm))) {

        // Open recordset
        rs = openrs( stat, sSQL);
        rs.next();
        String[] aFields = getFieldsName( rs );
        getRecordToHash( rs, rsHash, aFields );
        rs.close();
        fldempid = (String) rsHash.get("empid");
        if ( "".equals(sempsErr)) {
          // Load data from recordset when form displayed first time
          fldage = (String) rsHash.get("age");
          fldcom = (String) rsHash.get("com");
          fldda = (String) rsHash.get("da");
          fldhra = (String) rsHash.get("hra");
          fldbasic = (String) rsHash.get("basic");
          flddepid = (String) rsHash.get("depid");
          
        }

        if (sAction.equals("") || ! "emps".equals(sForm)) {
      
          fldage = (String) rsHash.get("age");
          fldcom = (String) rsHash.get("com");
          fldda = (String) rsHash.get("da");
          fldhra = (String) rsHash.get("hra");
          fldbasic = (String) rsHash.get("basic");
          flddepid = (String) rsHash.get("depid");
        }
        
      }
      else {
        if ( "".equals(sempsErr)) {
          fldempid = toHTML(getParam(request,"empid"));
        }
      }
      


      // Show form field
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Name</font></td><td >"); out.print("<input type=\"text\"  name=\"name\" maxlength=\"100\" value=\""+toHTML(fldname)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Title</font></td><td >"); out.print("<input type=\"text\"  name=\"title\" maxlength=\"50\" value=\""+toHTML(fldtitle)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Login</font></td><td >"); out.print("<input type=\"text\"  name=\"emp_login\" maxlength=\"20\" value=\""+toHTML(fldemp_login)+"\" size=\"20\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Password</font></td><td >"); out.print("<input type=\"password\"  name=\"emp_password\" maxlength=\"20\" value=\""+toHTML(fldemp_password)+"\" size=\"20\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Level</font></td><td >"); 
      out.print("<select name=\"emp_level\">"+getOptionsLOV("0;None;3;Admin",false,true,fldemp_level)+"</select>");
      
      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Department</font></td><td >"); 
      out.print("<select name=\"dep_id\">"+getOptions( conn, "select dep_id, name from deps order by 2",false,true,flddep_id)+"</select>");
      
      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Address</font></td><td >"); out.print("<textarea name=\"address\" cols=\"50\" rows=\"2\">"+toHTML(fldaddress)+"</textarea>");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Email</font></td><td >"); out.print("<input type=\"text\"  name=\"email\" maxlength=\"50\" value=\""+toHTML(fldemail)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Work Phone</font></td><td >"); out.print("<input type=\"text\"  name=\"work_phone\" maxlength=\"50\" value=\""+toHTML(fldwork_phone)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Home Phone</font></td><td >"); out.print("<input type=\"text\"  name=\"home_phone\" maxlength=\"50\" value=\""+toHTML(fldhome_phone)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Cell Phone</font></td><td >"); out.print("<input type=\"text\"  name=\"cell_phone\" maxlength=\"50\" value=\""+toHTML(fldcell_phone)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Man of the Month</font></td><td >"); 
      if ( fldmanmonth.equalsIgnoreCase("1") ) {
        out.print("<input checked type=\"checkbox\" name=\"manmonth\" value=\"1\">");
      }
      else {
        out.print("<input type=\"checkbox\" name=\"manmonth\" value=\"1\">");
      }
      
      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Picture</font></td><td >"); out.print("<input type=\"text\"  name=\"picture\" maxlength=\"100\" value=\""+toHTML(fldpicture)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td colspan=\"2\" align=\"right\">");
      

      if ( bPK && ! (sAction.equals("insert") && "emps".equals(sForm))) {
        out.print("<input type=\"submit\" value=\"Update\" onclick=\"document.emps.FormAction.value = 'update';\">");out.print("<input type=\"submit\" value=\"Delete\" onclick=\"document.emps.FormAction.value = 'delete';\">");out.print("<input type=\"submit\" value=\"Cancel\" onclick=\"document.emps.FormAction.value = 'cancel';\">");
        out.print("<input type=\"hidden\" name=\"FormName\" value=\"emps\"><input type=\"hidden\" value=\"update\" name=\"FormAction\">");
      }
      
      else {
        out.print("<input type=\"submit\" value=\"Insert\" onclick=\"document.emps.FormAction.value = 'insert';\">");out.print("<input type=\"submit\" value=\"Cancel\" onclick=\"document.emps.FormAction.value = 'cancel';\">");
        out.print("<input type=\"hidden\" name=\"FormName\" value=\"emps\"><input type=\"hidden\" value=\"insert\" name=\"FormAction\">");
      }out.print("<input type=\"hidden\" name=\"emp_id\" value=\""+toHTML(fldempid)+"\">");
      out.print(transitParamsHidden+requiredParams+primaryKeyParams);
      out.println("</td>\n     </tr>\n     </form>\n    </table>");
      



    }
    catch (Exception e) { out.println(e.toString()); }
  } %>