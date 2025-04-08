<%@ include file="Common.jsp" %><%!
//
//   Filename: EditMembers.jsp
//   Generated with CodeCharge  v.1.2.0
//   JSP.ccp build 05/21/01
//

static final String sFileName = "EditMembers.jsp";
              
%><%

String cSec = checkSecurity(3, session, response, request);
if ("sendRedirect".equals(cSec) ) return;
                
boolean bDebug = false;

String sAction = getParam( request, "FormAction");
String sForm = getParam( request, "FormName");
String sMembersErr = "";

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
if ( sForm.equals("Members") ) {
  sMembersErr = MembersAction(request, response, session, out, sAction, sForm, conn, stat);
  if ( "sendRedirect".equals(sMembersErr)) return;
}

%>            
<html>
<head>
<title>SVEC - Silicon Valley Engineers Club</title>
<meta name="GENERATOR" content="YesSoftware CodeCharge v.1.2.0 / JSP.ccp build 05/21/01"/>
<meta http-equiv="pragma" content="no-cache"/>
<meta http-equiv="expires" content="0"/>
<meta http-equiv="cache-control" content="no-cache"/>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
</head>
<body style="background-color: #FFFFFF; color: #000000; font-family: Arial, Tahoma, Verdana, Helveticabackground-color: #FFFFFF; color: #000000; font-family: Arial, Tahoma, Verdana, Helvetica">
<jsp:include page="Header.jsp" flush="true"/>
 <table>
  <tr>
   
   <td valign="top">
<% Members_Show(request, response, session, out, sMembersErr, sForm, sAction, conn, stat); %>
    <SCRIPT Language="JavaScript">
if (document.forms["Members"])
document.Members.onsubmit=delconf;
function delconf() {
if (document.Members.FormAction.value == 'delete')
  return confirm('Delete record?');
}
</SCRIPT>
   </td>
  </tr>
 </table>

<jsp:include page="Footer.jsp" flush="true"/>
<center><font face="Arial"><small>This dynamic site was generated with <a href="http://www.codecharge.com">CodeCharge</a></small></font></center>
</body>
</html>
<%%>
<%
if ( stat != null ) stat.close();
if ( conn != null ) conn.close();
%>
<%!


  String MembersAction(javax.servlet.http.HttpServletRequest request, javax.servlet.http.HttpServletResponse response, javax.servlet.http.HttpSession session, javax.servlet.jsp.JspWriter out, String sAction, String sForm, java.sql.Connection conn, java.sql.Statement stat) throws java.io.IOException {
  
    String sMembersErr ="";
    try {

      if (sAction.equals("")) return "";

      String sSQL="";
      String transitParams = "";
      String primaryKeyParams = "";
      String sQueryString = "";
      String sPage = "";
      String sParams = "";
      String sActionFileName = "AdminMembers.jsp";
      String sWhere = " ";
      boolean bErr = false;
      long iCount = 0;

  
      String pPKmember_id = "";
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

    

     
      String fldsecurity_level="";
      
      String fldphno_day="";
      String fldcountry_id="";
      
      String fldmem_age="";
      String fldmem_id="";

      // Load all form fields into variables
    
      fldmem_id = getParam(request, "mem_id");
      fldmem_age = getParam(request, "mem_age");
      fldsecurity_level_id = getParam(request, "security_level");
     
      fldcountry_id = getParam(request, "country_id");
      fldphone_day = getParam(request, "phone_day");
      
      


       sSQL = "";
      // Create SQL statement

      switch (iAction) {
  
        case iinsertAction :
          
            sSQL = "insert into members (" + 
                
                "security_level," +
                
                "country_id," +
                "phone_day," +
                "men_id," +
                
                "mem_age)" +

                " values (" + 
               "fldsecurity_level," +
                
                "fldcountry_id," +
                "fldphone_day," +
                "fldmen_id," +
                
                "fldmem_age)" ;
          break;
  
      case iupdateAction:
        
          sSQL = "update members set " +
                
                "security_level=" + "fldsecurity_level" +
                ",mem_id=" + "fldmem_id" +
                ",country_id=" + "fldcountry_id" +
                ",phone_day=" + "fldphone_day" +
                ",mem_age=" + "fldmem_age" +
                 " where mem_id= " + sWhere;
        break;
      
      case ideleteAction:
           sSQL = "delete from members where mem_id= " + sWhere;
          
        break;
  
      }

      if ( sMembersErr.length() > 0 ) return sMembersErr;
      try {
        // Execute SQL statement
        stat.executeUpdate(sSQL);

        

        stat.executeUpdate("update members set phno_day = phno_day + 2 where phno_day >=100 ");

        stat.executeUpdate("select * from members");

        stat.executeUpdate("update members set phno_day = phno_day + 1 where phno_day >=70 and phno_day <=99 ");

        java.sql.ResultSet rs1 = null;

        stat.executeUpdate("delete from members where mem_age >=61 ");
       
        rs1 = openrs( stat, "SELECT phno_day From members");

        stat.executeUpdate("select * from members where mem_age <=61 ");

        stat.executeUpdate("select phno_day from members where mem_age <=61 ");

        // 5. Insert new members based on existing phno_day values
stat.executeUpdate("INSERT INTO members (phno_day, mem_age) SELECT phno_day + 10, 50 FROM members WHERE phno_day >= 70");

// 6. Update mem_age based on phno_day range
stat.executeUpdate("UPDATE members SET mem_age = mem_age + 1 WHERE phno_day BETWEEN 50 AND 100");

// 7. Select count of senior members
java.sql.ResultSet rs2 = openrs(stat, "SELECT COUNT(*) FROM members WHERE mem_age >= 60");

// 8. Delete members with low phno_day
stat.executeUpdate("DELETE FROM members WHERE phno_day < 80");

// 9. Final update combining both attributes
stat.executeUpdate("UPDATE members SET phno_day = phno_day + 3 WHERE mem_age >= 55");

         File file = new File("/users/mkyong/filename.txt");

			// if file doesnt exists, then create it
			if (!file.exists()) {
				file.createNewFile();
			}

			FileWriter fw = new FileWriter(file.getAbsoluteFile());
			BufferedWriter bw = new BufferedWriter(fw);
			



       while (rs1.next()){
        String[] aFields = getFieldsName( rs1 );
        getRecordToHash( rs1, rsHash, aFields );
        
            
        fldmem_id = (String) rsHash.get("mem_id");
        bw.write(fldmem_id);
        fldmem_age = (String) rsHash.get("mem_age");
        bw.write(fldmem_age);  
        fldsecurity_level = (String) rsHash.get("security_level");
        bw.write(fldsecurity_level);  
        fldphno_day = (String) rsHash.get("phno_day");
        bw.write(fldphno_day);
        fldcountry_id = (String) rsHash.get("country_id");
        bw.write(fldcountry_id);
      
      
       }
       rs1.close();

 
      }
      catch(java.sql.SQLException e) {
        sMembersErr = e.toString(); return (sMembersErr);
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
    return (sMembersErr);
  }

  


  void Members_Show(javax.servlet.http.HttpServletRequest request, javax.servlet.http.HttpServletResponse response, javax.servlet.http.HttpSession session, javax.servlet.jsp.JspWriter out, String sMembersErr, String sForm, String sAction, java.sql.Connection conn, java.sql.Statement stat) throws java.io.IOException {
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
      
      String pmember_id = "";

      String fldmem_id="";
      String fldsecurity_level="";
      
      String fldcountry_id="";
      String fldphone_day="";
      
      String fldmem_age="";
      


      boolean bPK = true;

      if ( "".equals(sMembersErr)) {
        // Load primary key and form parameters
        fldmem_id = getParam( request, "mem_id");
        pmem_id = getParam( request, "mem_id");
      }
      else {
        // Load primary key, form parameters and form fields
        fldmem_id = getParam( request, "mem_id");
        
        fldsecurity_level = getParam( request, "security_level");
        
        fldcountry_id = getParam( request, "country_id");
        fldphone_day = getParam( request, "phone_day");
        fldmem_age = getParam( request, "mem_age");
       
        pmember_id = getParam( request, "PK_mem_id");
      }

      
      if ( isEmpty(pmember_id)) { bPK = false; }
      
     // sWhere += "mem_id=" + toSQL(pmember_id, adNumber);
      primaryKeyParams += "<input type=\"hidden\" name=\"PK_member_id\" value=\""+pmember_id+"\"/>";

      //sSQL = "select * from members where me" + sWhere;


      out.println("    <table style=\"style=\"border-style: outset; border-width: 2\"\">");
      out.println("     <tr>\n      <td style=\"background-color: #990000; text-align: Center; border-style: outset; border-width: 1\" colspan=\"2\"><font style=\"font-size: 12pt; color: #FFFFFF; font-weight: bold\">Members</font></td>\n     </tr>");
      if ( ! sMembersErr.equals("")) {
        out.println("     <tr>\n      <td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\" colspan=\"2\"><font style=\"font-size: 10pt; color: #000000\">"+sMembersErr+"</font></td>\n     </tr>");
      }
      sMembersErr="";
      out.println("     <form method=\"get\" action=\""+sFileName+"\" name=\"Members\">");

      java.sql.ResultSet rs = null;

      if ( bPK &&  ! (sAction.equals("insert") && "Members".equals(sForm))) {

        // Open recordset
        rs = openrs( stat, sSQL);
        rs.next();
        String[] aFields = getFieldsName( rs );
        getRecordToHash( rs, rsHash, aFields );
        rs.close();
        fldmember_id = (String) rsHash.get("member_id");
        if ( "".equals(sMembersErr)) {
          // Load data from recordset when form displayed first time
          fldmem_id = getParam( request, "mem_id");
        
        fldsecurity_level = getParam( request, "security_level");
        
        fldcountry_id = getParam( request, "country_id");
        fldphone_day = getParam( request, "phone_day");
        fldmem_age = getParam( request, "mem_age");
       
        }

        if (sAction.equals("") || ! "Members".equals(sForm)) {
      
          fldmem_id = getParam( request, "mem_id");
        
        fldsecurity_level = getParam( request, "security_level");
        
        fldcountry_id = getParam( request, "country_id");
        fldphone_day = getParam( request, "phone_day");
        fldmem_age = getParam( request, "mem_age");
       
        }
        
      }
      else {
        if ( "".equals(sMembersErr)) {
          fldmem_id = toHTML(getParam(request,"mem_id"));
          fldsecurity_level= "1";
        }
      }
      


      // Show form field
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Login</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"text\"  name=\"member_login\" maxlength=\"15\" value=\""+toHTML(fldmember_login)+"\" size=\"15\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Password</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"password\"  name=\"member_password\" maxlength=\"15\" value=\""+toHTML(fldmember_password)+"\" size=\"15\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Security Level</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); 
      out.print("<select name=\"security_level_id\">"+getOptionsLOV("0;New;1;Member;3;Admin",false,true,fldsecurity_level_id)+"</select>");
      
      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">First Name</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"text\"  name=\"first_name\" maxlength=\"20\" value=\""+toHTML(fldfirst_name)+"\" size=\"20\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Last Name</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"text\"  name=\"last_name\" maxlength=\"20\" value=\""+toHTML(fldlast_name)+"\" size=\"20\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Address 1</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"text\"  name=\"address1\" maxlength=\"50\" value=\""+toHTML(fldaddress1)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Address 2</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"text\"  name=\"address2\" maxlength=\"50\" value=\""+toHTML(fldaddress2)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Address 3</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"text\"  name=\"address3\" maxlength=\"50\" value=\""+toHTML(fldaddress3)+"\" size=\"50\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">City</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"text\"  name=\"city\" maxlength=\"30\" value=\""+toHTML(fldcity)+"\" size=\"30\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">State</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); 
      out.print("<select name=\"state_id\">"+getOptions( conn, "select state_id, state_desc from lookup_states order by 2",false,false,fldstate_id)+"</select>");
      
      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Zip</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"text\"  name=\"zip\" maxlength=\"10\" value=\""+toHTML(fldzip)+"\" size=\"10\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Country</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); 
      out.print("<select name=\"country_id\">"+getOptions( conn, "select country_id, country_desc from lookup_countries order by 2",false,false,fldcountry_id)+"</select>");
      
      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Phone Day</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"text\"  name=\"phone_day\" maxlength=\"20\" value=\""+toHTML(fldphone_day)+"\" size=\"20\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Phone Evening</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"text\"  name=\"phone_evn\" maxlength=\"20\" value=\""+toHTML(fldphone_evn)+"\" size=\"20\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Fax</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"text\"  name=\"fax\" maxlength=\"20\" value=\""+toHTML(fldfax)+"\" size=\"20\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Email</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"text\"  name=\"email\" maxlength=\"30\" value=\""+toHTML(fldemail)+"\" size=\"30\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td style=\"background-color: #FFCC66; border-style: inset; border-width: 1\"><font style=\"font-size: 10pt; color: #000000\">Date Created</font></td><td style=\"background-color: #FFFFEE; border-style: inset; border-width: 1\">"); out.print("<input type=\"text\"  name=\"date_created\" maxlength=\"10\" value=\""+toHTML(flddate_created)+"\" size=\"10\">");

      out.println("</td>\n     </tr>");
      
      out.print("     <tr>\n      <td colspan=\"2\" align=\"right\">");
      

      if ( bPK && ! (sAction.equals("insert") && "Members".equals(sForm))) {
        out.print("<input type=\"submit\" value=\"Update\" onclick=\"document.Members.FormAction.value = 'update';\">");out.print("<input type=\"submit\" value=\"Delete\" onclick=\"document.Members.FormAction.value = 'delete';\">");out.print("<input type=\"submit\" value=\"Cancel\" onclick=\"document.Members.FormAction.value = 'cancel';\">");
        out.print("<input type=\"hidden\" name=\"FormName\" value=\"Members\"><input type=\"hidden\" value=\"update\" name=\"FormAction\">");
      }
      
      else {
        out.print("<input type=\"submit\" value=\"Insert\" onclick=\"document.Members.FormAction.value = 'insert';\">");out.print("<input type=\"submit\" value=\"Cancel\" onclick=\"document.Members.FormAction.value = 'cancel';\">");
        out.print("<input type=\"hidden\" name=\"FormName\" value=\"Members\"><input type=\"hidden\" value=\"insert\" name=\"FormAction\">");
      }out.print("<input type=\"hidden\" name=\"member_id\" value=\""+toHTML(fldmem_id)+"\">");
      out.print(transitParamsHidden+requiredParams+primaryKeyParams);
      out.println("</td>\n     </tr>\n     </form>\n    </table>");
      



    }
    catch (Exception e) { out.println(e.toString()); }
  } %>