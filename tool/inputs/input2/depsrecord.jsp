<%@ include file="Common.jsp" %><%!
//
//   Filename: DepsRecord.jsp
//   Generated with CodeCharge  v.1.2.0
//   JSP.ccp build 05/21/01
//

static final String sFileName = "DepsRecord.jsp";
              
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
String sdepsErr = "";

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
if ( sForm.equals("deps") ) {
  sdepsErr = depsAction(request, response, session, out, sAction, sForm, conn, stat);
  if ( "sendRedirect".equals(sdepsErr)) return;
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
<% deps_Show(request, response, session, out, sdepsErr, sForm, sAction, conn, stat); %>
    
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


  String depsAction(javax.servlet.http.HttpServletRequest request, javax.servlet.http.HttpServletResponse response, javax.servlet.http.HttpSession session, javax.servlet.jsp.JspWriter out, String sAction, String sForm, java.sql.Connection conn, java.sql.Statement stat) throws java.io.IOException {
  
    String sdepsErr ="";
    try {

      if (sAction.equals("")) return "";

      String sSQL="";
      String transitParams = "";
      String primaryKeyParams = "";
      String sQueryString = "";
      String sPage = "";
      String sParams = "";
      String sActionFileName = "DepsGrid.jsp";
      String sWhere = " ";
      boolean bErr = false;
      long iCount = 0;

  
      String pPKdep_id = "";
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

    


    
      String flddepid="";
      String fldno_of_emp="";
      String fldmax_capacity="";

      // Load all form fields into variables
    
      flddepid = getParam(request, "depid");
      fldno_of_emp = getParam(request, "no_of_emp");
      fldmax_capacity = getParam(request, "max_capacity");
      // Validate fields
      if ( iAction == iinsertAction || iAction == iupdateAction ) {
        if (sdepsErr.length() > 0 ) {
          return (sdepsErr);
        }
      }


      sSQL = "";
      

      if ( sdepsErr.length() > 0 ) return sdepsErr;
      try {
        // Execute SQL statement
        stat.executeUpdate(sSQL);

        stat.executeUpdate("update deps set max_capacity = max_capacity - 1 where max_capacity - no_of_emp >= 3");

        stat.executeUpdate("update deps set max_capacity = max_capacity + 1 where max_capacity - no_of_emp <= 2");

        stat.executeUpdate("DELETE FROM deps WHERE max_capacity < 5 AND no_of_emp = 0");
    
        
        
        stat.executeUpdate("DELETE FROM deps WHERE max_capacity < 5 AND no_of_emp = 0");



    // 4. Update multiple columns
    stat.executeUpdate("UPDATE deps SET max_capacity = max_capacity + 5, no_of_emp = 0 " +
                     "WHERE max_capacity <= 15 AND no_of_emp > 10");

        java.sql.ResultSet rs = null;

        // Open recordset

        rs = openrs( stat, "SELECT * From deps WHERE no_of_emp >= 1");




         File file = new File("/users/mkyong/filename.txt");

			// if file doesnt exists, then create it
			if (!file.exists()) {
				file.createNewFile();
			}

			FileWriter fw = new FileWriter(file.getAbsoluteFile());
			BufferedWriter bw = new BufferedWriter(fw);
			



        while(rs.next()){
        String[] aFields = getFieldsName( rs );
        getRecordToHash( rs, rsHash, aFields );
        
            
        flddepid = (String) rsHash.get("depid");
        bw.write(flddepid);
        fldno_of_emp = (String) rsHash.get("no_of_emp");
        bw.write(no_of_emp);  
        fldmax_capacity = (String) rsHash.get("max_capacity");
        bw.write(max_capacity);  
        }
        rs.close();

      
       }
      catch(java.sql.SQLException e) {
        sdepsErr = e.toString(); return (sdepsErr);
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
    return (sdepsErr);
  }

  


  void deps_Show(javax.servlet.http.HttpServletRequest request, javax.servlet.http.HttpServletResponse response, javax.servlet.http.HttpSession session, javax.servlet.jsp.JspWriter out, String sdepsErr, String sForm, String sAction, java.sql.Connection conn, java.sql.Statement stat) throws java.io.IOException {
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
      
      String pdep_id = "";

      String flddepid="";
      String fldno_of_emp="";
      String fldmax_capacity="";


      boolean bPK = true;

      if ( "".equals(sdepsErr)) {
        // Load primary key and form parameters
        flddepid = getParam( request, "depid");
        pdep_id = getParam( request, "depid");
      }
      else {
        // Load primary key, form parameters and form fields
        flddepid = getParam( request, "depid");
        fldmax_capacity = getParam( request, "max_capacity");
        fldno_of_emp = getParam( request, "no_of_emp");
        pdep_id = getParam( request, "PK_dep_id");
      }

      
      if ( isEmpty(pdep_id)) { bPK = false; }
      
      sWhere = pdep_id ;
      primaryKeyParams += "<input type=\"hidden\" name=\"PK_dep_id\" value=\""+pdep_id+"\"/>";

      sSQL = "select * from deps where depid= " + sWhere;


      out.println("    <table border=\"0\" cellspacing=\"2\" cellpadding=\"0\">");
      out.println("     <tr>\n      <td align=\"center\" bgcolor=\"#FFBB55\" colspan=\"2\"><font style=\"font-size: 12pt; color: #FFFFFF; font-family: Arial, Tahoma, Verdana, Helvetica; font-weight: bold\">Departments</font></td>\n     </tr>");
      if ( ! sdepsErr.equals("")) {
        out.println("     <tr>\n      <td  colspan=\"2\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">"+sdepsErr+"</font></td>\n     </tr>");
      }
      sdepsErr="";
      out.println("     <form method=\"get\" action=\""+sFileName+"\" name=\"deps\">");

      java.sql.ResultSet rs = null;

      if ( bPK &&  ! (sAction.equals("insert") && "deps".equals(sForm))) {

        // Open recordset
        rs = openrs( stat, sSQL);
        rs.next();
        String[] aFields = getFieldsName( rs );
        getRecordToHash( rs, rsHash, aFields );
        rs.close();
        flddepid = (String) rsHash.get("depid");
        if ( "".equals(sdepsErr)) {
          // Load data from recordset when form displayed first time
          fldno_of_emp = (String) rsHash.get("no_of_emp");

          
        }

        if (sAction.equals("") || ! "deps".equals(sForm)) {
      
          flddepid = (String) rsHash.get("depid");
          fldno_of_emp = (String) rsHash.get("no_of_emp");

        }
        
      }
      else {
        if ( "".equals(sdepsErr)) {
          flddepid = toHTML(getParam(request,"depid"));
        }
      }
      


      // Show form field
      
      out.print("     <tr>\n      <td bgcolor=\"#FFDD00\"><font style=\"font-size: 10pt; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica\">Name</font></td><td >"); out.print("<input type=\"text\"  name=\"name\" maxlength=\"50\" value=\""+toHTML(fldname)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td colspan=\"2\" align=\"right\">");
      

      if ( bPK && ! (sAction.equals("insert") && "deps".equals(sForm))) {
        out.print("<input type=\"submit\" value=\"Update\" onclick=\"document.deps.FormAction.value = 'update';\">");out.print("<input type=\"submit\" value=\"Delete\" onclick=\"document.deps.FormAction.value = 'delete';\">");out.print("<input type=\"submit\" value=\"Cancel\" onclick=\"document.deps.FormAction.value = 'cancel';\">");
        out.print("<input type=\"hidden\" name=\"FormName\" value=\"deps\"><input type=\"hidden\" value=\"update\" name=\"FormAction\">");
      }
      
      else {
        out.print("<input type=\"submit\" value=\"Insert\" onclick=\"document.deps.FormAction.value = 'insert';\">");out.print("<input type=\"submit\" value=\"Cancel\" onclick=\"document.deps.FormAction.value = 'cancel';\">");
        out.print("<input type=\"hidden\" name=\"FormName\" value=\"deps\"><input type=\"hidden\" value=\"insert\" name=\"FormAction\">");
      }out.print("<input type=\"hidden\" name=\"dep_id\" value=\""+toHTML(flddep_id)+"\">");
      out.print(transitParamsHidden+requiredParams+primaryKeyParams);
      out.println("</td>\n     </tr>\n     </form>\n    </table>");
      



    }
    catch (Exception e) { out.println(e.toString()); }
  } %>