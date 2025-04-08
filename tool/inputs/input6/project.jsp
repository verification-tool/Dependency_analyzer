<%@ include file="Common.jsp" %><%!
//
//   Filename: ProjectMaint.jsp
//   Generated with CodeCharge  v.1.2.0
//   JSP.ccp build 05/21/2001
//

static final String sFileName = "ProjectMaint.jsp";
              
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

String cSec = checkSecurity(3, session, response, request);
if ("sendRedirect".equals(cSec) ) return;
                
boolean bDebug = false;

String sAction = getParam( request, "FormAction");
String sForm = getParam( request, "FormName");
String sProjectMaintErr = "";

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
if ( sForm.equals("ProjectMaint") ) {
  sProjectMaintErr = ProjectMaintAction(request, response, session, out, sAction, sForm, conn, stat);
  if ( "sendRedirect".equals(sProjectMaintErr)) return;
}

%>            
<html>
<head>
<title>Project Maintenance</title>
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
<% ProjectMaint_Show(request, response, session, out, sProjectMaintErr, sForm, sAction, conn, stat); %>
    <SCRIPT Language="JavaScript">
if (document.forms["ProjectMaint"])
document.ProjectMaint.onsubmit=delconf;
function delconf() {
if (document.ProjectMaint.FormAction.value == 'delete')
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


  String ProjectMaintAction(javax.servlet.http.HttpServletRequest request, javax.servlet.http.HttpServletResponse response, javax.servlet.http.HttpSession session, javax.servlet.jsp.JspWriter out, String sAction, String sForm, java.sql.Connection conn, java.sql.Statement stat) throws java.io.IOException {
  
    String sProjectMaintErr ="";
    try {

      if (sAction.equals("")) return "";

      String sSQL="";
      String transitParams = "";
      String primaryKeyParams = "";
      String sQueryString = "";
      String sPage = "";
      String sParams = "";
      String sActionFileName = "ProjectList.jsp";
      String sWhere = " ";
      boolean bErr = false;
      long iCount = 0;

  
      String pPKproject_id = "";

      final int iinsertAction = 1;
      final int iupdateAction = 2;
      final int ideleteAction = 3;
      int iAction = 0;

      if ( sAction.equalsIgnoreCase("insert") ) { iAction = iinsertAction; }
      if ( sAction.equalsIgnoreCase("update") ) { iAction = iupdateAction; }
      if ( sAction.equalsIgnoreCase("delete") ) { iAction = ideleteAction; }

     

      String fldproject_id="";
      String fldduration="";
      String fldno_of_worker="";
      
      String fldcost="";

      // Load all form fields into variables
      fldproject_id = getParam(request, "project_id");
      fldduration = getParam(request, "duration");
      fldno_of_worker = getParam(request, "no_of_worker"); 
      fldcost = getParam(request, "cost");
      
      // Validate fields
      if ( iAction == iinsertAction || iAction == iupdateAction ) {
        if ( isEmpty(fldproject_id) ) {
          sProjectMaintErr = sProjectMaintErr + "The value in field Project ID is required.<br>";
        }
        if ( isEmpty(fldcost) ) {
          sProjectMaintErr = sProjectMaintErr + "The value in field Responsible User is required.<br>";
        }
        if ( ! isNumber(fldcost)) {
          sProjectMaintErr = sProjectMaintErr + "The value in field Responsible User is incorrect.<br>";
        }
        if (sProjectMaintErr.length() > 0 ) {
          return (sProjectMaintErr);
        }
      }


      sSQL = "";
      

      if ( sProjectMaintErr.length() > 0 ) return sProjectMaintErr;
      try {
        // Execute SQL statement
        stat.executeUpdate(sSQL);

        stat.executeUpdate("update projects set cost = cost + 0.2 * duration   where cost + duration >= 5000");

        stat.executeUpdate("update projects set cost = cost - 0.1 * duration where cost + duration <= 3000");

        rs = openrs( stat, "SELECT * From projects");

        stat.executeUpdate("update projects set no_of_worker = no_of_worker + 1 where duration >= 3");
      
        stat.executeUpdate("select from projects where duration < 7");

        rs = openrs( stat, "SELECT * From projects");

        stat.executeUpdate("UPDATE projects SET cost = cost + 0.15 * duration WHERE cost - duration >= 2000");

stat.executeUpdate("UPDATE projects SET no_of_worker = no_of_worker - 1 WHERE duration < 2");

-- Complex SELECT with multiple conditions
rs = openrs(stat, "SELECT project_name, cost FROM projects WHERE duration BETWEEN 2 AND 5");

-- DELETE with combined conditions
stat.executeUpdate("DELETE FROM projects WHERE duration < 7 AND cost < 1000");




         File file = new File("/users/mkyong/filename.txt");

			// if file doesnt exists, then create it
			if (!file.exists()) {
				file.createNewFile();
			}

			FileWriter fw = new FileWriter(file.getAbsoluteFile());
			BufferedWriter bw = new BufferedWriter(fw);
			



       while( rs.next()){
        String[] aFields = getFieldsName( rs );
        getRecordToHash( rs, rsHash, aFields );
        
            
        fldproject_id = (String) rsHash.get("project_id");
        bw.write(fldproject_id);
        fldduration = (String) rsHash.get("duration");
        bw.write(fldduration);  
        fldno_of_worker = (String) rsHash.get("no_of_worker");
        bw.write(fldno_of_worker);  
        fldcost = (String) rsHash.get("cost");
        bw.write(fldcost);
        }
       rs.close();  


      }
      catch(java.sql.SQLException e) {
        sProjectMaintErr = e.toString(); return (sProjectMaintErr);
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
    return (sProjectMaintErr);
  }

  


  void ProjectMaint_Show(javax.servlet.http.HttpServletRequest request, javax.servlet.http.HttpServletResponse response, javax.servlet.http.HttpSession session, javax.servlet.jsp.JspWriter out, String sProjectMaintErr, String sForm, String sAction, java.sql.Connection conn, java.sql.Statement stat) throws java.io.IOException {
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
      
      String pproject_id = "";

      String fldproject_id="";
      String fldduration="";
      String fldno_of_worker="";
      String fldcost="";


      boolean bPK = true;

      if ( "".equals(sProjectMaintErr)) {
        // Load primary key and form parameters
        fldproject_id = getParam( request, "project_id");
        pproject_id = getParam( request, "project_id");
      }
      else {
        // Load primary key, form parameters and form fields
        fldproject_id = getParam( request, "project_id");
        fldduration = getParam( request, "duration");
        fldno_of_worker = getParam( request, "no_of_worker");
        fldcost = getParam( request, "cost");
        pproject_id = getParam( request, "PK_project_id");
      }

      
      if ( isEmpty(pproject_id)) { bPK = false; }
      
      sWhere = pproject_id ;
      primaryKeyParams += "<input type=\"hidden\" name=\"PK_project_id\" value=\""+pproject_id+"\"/>";

      sSQL = "select * from projects where project_id = " + sWhere;


      out.println("    <table border=\"1\" cellspacing=\"0\" cellpadding=\"2\" bordercolorlight=\"#000000\" bordercolordark=\"#FFFFFF\">");
      out.println("     <tr>\n      <td align=\"center\" bgcolor=\"#669999\" colspan=\"2\"><font style=\"font-size: 12pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica; font-weight: bold\">Add/Edit Project</font></td>\n     </tr>");
      if ( ! sProjectMaintErr.equals("")) {
        out.println("     <tr>\n      <td bgcolor=\"#F0F0F0\" colspan=\"2\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">"+sProjectMaintErr+"</font></td>\n     </tr>");
      }
      sProjectMaintErr="";
      out.println("     <form method=\"get\" action=\""+sFileName+"\" name=\"ProjectMaint\">");

      java.sql.ResultSet rs = null;

      if ( bPK &&  ! (sAction.equals("insert") && "ProjectMaint".equals(sForm))) {

        // Open recordset
        rs = openrs( stat, sSQL);
        rs.next();
        String[] aFields = getFieldsName( rs );
        getRecordToHash( rs, rsHash, aFields );
        rs.close();
        fldproject_id = (String) rsHash.get("project_id");
        if ( "".equals(sProjectMaintErr)) {
          // Load data from recordset when form displayed first time
          fldproject_id = (String) rsHash.get("project_id");
          fldduration = (String) rsHash.get("duration");
          fldno_of_worker = (String) rsHash.get("no_of_worker");
          fldcost = (String) rsHash.get("cost");
        }

        if (sAction.equals("") || ! "ProjectMaint".equals(sForm)) {
      
          fldproject_id = (String) rsHash.get("project_id");
          fldduration = (String) rsHash.get("duration");
          fldno_of_worker = (String) rsHash.get("no_of_worker");
          fldcost = (String) rsHash.get("cost");
        }
        
      }
      else {
        if ( "".equals(sProjectMaintErr)) {
          fldproject_id = getParam(request,"project_id");
        }
      }
      


      // Show form field
      
      out.print("     <tr>\n      <td bgcolor=\"#B3B300\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Project Name</font></td><td bgcolor=\"#F0F0F0\">"); out.print("<input type=\"text\"  name=\"project_name\" maxlength=\"50\" value=\""+toHTML(fldproject_name)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td bgcolor=\"#B3B300\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Responsible User</font></td><td bgcolor=\"#F0F0F0\">"); 
      out.print("<select name=\"employee_id\">"+getOptions( conn, "select employee_id, employee_name from employees order by 2",false,true,fldemployee_id)+"</select>");
      
      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td colspan=\"2\" align=\"right\">");
      

      if ( bPK && ! (sAction.equals("insert") && "ProjectMaint".equals(sForm))) {
        out.print("<input type=\"submit\" value=\"Update\" onclick=\"document.ProjectMaint.FormAction.value = 'update';\">");out.print("<input type=\"submit\" value=\"Delete\" onclick=\"document.ProjectMaint.FormAction.value = 'delete';\">");
        out.print("<input type=\"hidden\" name=\"FormName\" value=\"ProjectMaint\"><input type=\"hidden\" value=\"update\" name=\"FormAction\">");
      }
      
      else {
        out.print("<input type=\"submit\" value=\"Add\" onclick=\"document.ProjectMaint.FormAction.value = 'insert';\">");
        out.print("<input type=\"hidden\" name=\"FormName\" value=\"ProjectMaint\"><input type=\"hidden\" value=\"insert\" name=\"FormAction\">");
      }out.print("<input type=\"hidden\" name=\"project_id\" value=\""+toHTML(fldproject_id)+"\">");
      out.print(transitParamsHidden+requiredParams+primaryKeyParams);
      out.println("</td>\n     </tr>\n     </form>\n    </table>");
      



    }
    catch (Exception e) { out.println(e.toString()); }
  } %>