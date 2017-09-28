Name: scitokens-credmon
Version: 0.1.0
Release: 1%{?dist}
Summary: SciTokens enabled CredMon for HTCondor

License: Apache 2.0
URL: https://github.com/opensciencegrid/SciTokens-CredMon

# Generated from:
# git archive v%{version} --prefix=scitokens-credmon-%{version}/ | gzip -7 > ~/rpmbuild/SOURCES/scitokens-credmon-%{version}.tar.gz
Source0: scitokens-credmon-0.1.0.tar.gz

BuildArch: noarch
Requires: python2-scitokens, condor-python

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}

%description
The CredMon is in charge of creating and renewing SciTokens on the submitter
and worker node. The CredMon has different behavior depending on whether it
detects it is running on a submitter or a execute node.

The CredMon detects whether it is running on the submitter or execute machine
by testing for the existance of the Private Key. If the private key is found,
the CredMon assumes it is on the Submitter. Otherwise, it is assumed to be on
the execute node.

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}/%{_bindir}
cp src/condor_credmon %{buildroot}/%{_bindir}

%files -n scitokens-credmon
%doc etc/example.conf
%{_bindir}/condor_credmon

%changelog
* Wed Sep 20 2017 Lincoln Bryant <lincolnb@uchicago.edu> - 0.1.0-1
- Initial package
