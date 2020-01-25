# TODO
# - check fedora progress: http://fedoraproject.org/wiki/Etherpad
#
# NOTE:
# tarfile created using hg:
# hg clone https://etherpad.googlecode.com/hg/ etherpad
# cd etherpad
# hg archive --type=tbz2 --prefix=%{name}-%{version} %{name}-%{version}-%{subver}.tar.bz2
%define		subver	20100429
%define		rel		0.1
Summary:	A web-based realtime collaborative document editor
Name:		etherpad
Version:	0
Release:	0.%{subver}%{rel}
License:	ASL 2.0
Group:		X11/Applications
URL:		http://code.google.com/p/etherpad/
Source0:	%{name}-%{version}-%{subver}.tar.bz2
# Source0-md5:	3dd182ec529c56f36ebcfe089389a7ac
Patch0:		%{name}-fix-paths.patch
#BuildRequires:	dnsjava
#BuildRequires:	jBCrypt
#BuildRequires:	jakarta-commons-lang
#BuildRequires:	java(javamail)
#BuildRequires:	java-1.6.0-openjdk-devel >= 1:1.6.0
#BuildRequires:	java-jcommon
#BuildRequires:	java-jfreechart
#BuildRequires:	jetty
BuildRequires:	jpackage-utils
#BuildRequires:	mysql-connector-java >= 5.1.0
#BuildRequires:	mysql-server
BuildRequires:	rpm-javaprov
BuildRequires:	rpmbuild(macros) >= 1.546
#BuildRequires:	scala >= 2.7
#BuildRequires:	tagsoup
#BuildRequires:	tomcat6-servlet-2.5-api
Requires:	jpackage-utils
Suggests:	mysql
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Open source release of EtherPad, a web-based realtime collaborative
document editor.

%prep
%setup -qc
mv etherpad-%{version}/trunk/* .
%patch0 -p1

# remove backup and git files
find -name '.gitignore' -exec rm -f '{}' \;
find -name '*.orig' -exec rm -f '{}' \;

# remove bundled libs and use our own ones
rm -f etherpad/lib/*
cp -p %{_javadir}/{dnsjava,jBCrypt,jcommon,jfreechart/jfreechart}.jar etherpad/lib/

# remove as many libs as we can right now
rm -f infrastructure/lib/{activation,commons-lang-2.4,dnsjava-2.0.6,jetty-6.1.20,jetty-util-6.1.21,mail,servlet-api-2.5-20081211,tagsoup-1.2,yuicompressor-2.4-appjet}.jar
cp %{_javadir}/{activation,commons-lang,dnsjava,jetty/jetty,jetty/jetty-util,javamail/mail,tomcat6-servlet-2.5-api,tagsoup}.jar infrastructure/lib/
# find a way to not hardcode the jetty version number here
cp %{_datadir}/jetty/lib/ext/jetty-sslengine-6.1.21.jar infrastructure/lib/

# rebuild modified yuicompressor instance
cd infrastructure/yuicompressor && ./make.sh && cd ../../

# adjust file permissions for rpmlint
chmod a+x infrastructure/bin/compilecache.sh
chmod a-x etherpad/src/static/js/jquery-1.2.6.js

# don't attempt to use growlnotify
sed -i -e 's/growlnotify/echo/g' etherpad/bin/rebuildjar.sh

# make sure to use appropriate arguments
sed -i -e 's/${mysql}/mysql/g' etherpad/bin/setup-mysql-db.sh

%build
export MYSQL_CONNECTOR_JAR="%{_javadir}/mysql-connector-java.jar"
export JAVA_HOME="%{_prefix}/java/jdk1.7.0"
export SCALA_HOME="%{_datadir}/scala"
cd etherpad
./bin/rebuildjar.sh

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_javadir}
cp -p etherpad/appjet-eth-dev.jar $RPM_BUILD_ROOT%{_javadir}/etherpad.jar

install -d $RPM_BUILD_ROOT%{_bindir}
cp -p etherpad/bin/rebuildjar.sh $RPM_BUILD_ROOT%{_bindir}/etherpad-rebuildjar.sh
cp -p etherpad/bin/run-local.sh $RPM_BUILD_ROOT%{_bindir}/etherpad-run-local.sh
cp -p etherpad/bin/setup-mysql-db.sh $RPM_BUILD_ROOT%{_bindir}/etherpad-setup-mysql-db.sh

install -d $RPM_BUILD_ROOT%{_sysconfdir}
cp -p etherpad%{_sysconfdir}/etherpad.localdev-default.properties $RPM_BUILD_ROOT%{_sysconfdir}/etherpad.localdev-default.properties

# remove bundled jar files and buildcache
rm -rf infrastructure/lib infrastructure/build infrastructure/buildcache

# create directories for run-local script
install -d $RPM_BUILD_ROOT%{_localstatedir}/log/etherpad
install -d $RPM_BUILD_ROOT%{_localstatedir}/run/etherpad

install -d $RPM_BUILD_ROOT%{_datadir}/etherpad
cp -pr etherpad/src infrastructure/* $RPM_BUILD_ROOT%{_datadir}/etherpad

# remove zero lengths files
find $RPM_BUILD_ROOT -size 0 | xargs rm -v

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc COPYING README
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/etherpad.localdev-default.properties
%attr(755,root,root) %{_bindir}/etherpad-*.sh
%{_datadir}/etherpad
%{_javadir}/etherpad.jar

%dir %{_localstatedir}/log/etherpad
%dir %{_localstatedir}/run/etherpad
