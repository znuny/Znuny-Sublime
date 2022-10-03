# --
# Copyright (C) 2012-2017 Znuny GmbH, http://znuny.com/
# --
# This software comes with ABSOLUTELY NO WARRANTY. For details, see
# the enclosed file COPYING for license information (AGPL). If you
# did not receive this file, see http://www.gnu.org/licenses/agpl.txt.
# --

package bin::ZnunyPODParser;

use strict;
use warnings;

use Pod::Parser;

our @ObjectDependencies = ();

our @ISA = qw(Pod::Parser);

=head1 NAME

bin::ZnunyPODParser - ZnunyPODParser lib

=head1 SYNOPSIS

All ZnunyPODParser functions

=head1 PUBLIC INTERFACE

=over 4

=cut

=head2 new()

create an object

    use bin::ZnunyPODParser;
    my $ZnunyPODParserObject = bin::ZnunyPODParser->new();

=cut

sub command {    ## no critic
    my ( $Parser, $Command, $Paragraph, $LineNum ) = @_;

    ## Interpret the command and its text; sample actions might be:
    my $OutFh = $Parser->output_handle();
    my $Expansion = $Parser->interpolate( $Paragraph, $LineNum );

    $Parser->{FunctionName} = undef;

    $Expansion =~ s{\n+\z}{}xms;

    return if $Expansion !~ m{\A(.+?)\(\)\z}xms;

    $Parser->{FunctionName} = $1;

    # for debugging purposes:
    # print $OutFh "-------------------\n";
    # print $OutFh "1: ". $Expansion ."\n";
}

sub verbatim {    ## no critic
    my ( $Parser, $Paragraph, $LineNum ) = @_;

    # for debugging purposes:
    # my $OutFh = $Parser->output_handle();
    # print $OutFh "2: ". $Paragraph ."\n";

    $Parser->{FunctionCalls} ||= {};

    my $ObjectName = $Parser->{FilesObjectMapping}->{$Parser->{_INFILE}};

    my $FunctionCallsRef = [];
    if ( $Parser->{FunctionName} && $Parser->{FunctionName} ne 'new' ) {
        $Parser->{FunctionCalls}->{ $Parser->{FunctionName} } ||= [];

        $FunctionCallsRef = $Parser->{FunctionCalls}->{ $Parser->{FunctionName} };
    }

    # this is needed because some Znuny framework PODs
    # have empty lines (e.g. Email->Send) or
    # comments (e.g. DynamicField->DynamicFieldList)
    # in them, which cause a new paragraph to spawn
    # therefore we have to check if we have a closing
    # function call, otherwise merge them into one
    if ( !$Parser->{UnfinishedFunction} ) {
        return if !$Parser->{FunctionName};
        return if $Paragraph !~ m{ $Parser->{FunctionName} \( }xms && $Parser->{FunctionName} ne 'new';

        # parse ObjectManager calls from new() pod
        if ( $Paragraph =~ m{(my \s \$ ([^\s]+) \s+ = \s+ \$Kernel::OM\->Get\(['"](.+)['"]\);)}x ) {

            # $1 = my $StateObject = $Kernel::OM->Get('Kernel::System::State');
            # $2 = StateObject
            # $3 = Kernel::System::State

            $Parser->{ObjectManager} = $1;
            $Parser->{ObjectName}    = $ObjectName // $2;
            $Parser->{Package}       = $3;

            return;
        }

        elsif ( $Paragraph =~ m{(my \s \$ ([^\s]+) \s+ = \s+ \$Kernel::OM\->Create\(\s*['"](.+)['"]\s*(?:,[^;]+)\);)}xms ) {

            # TODO: There might be multiple initialization possiblities
            #       Might check if the ObjectParams stuff can be 'snippetized'
            # $1 = my $CommunicationLogObject = $Kernel::OM->Create(
            #         'Kernel::System::CommunicationLog',
            #         ObjectParams => {
            #             Transport => 'Email',
            #             Direction => 'Incoming',
            #         }
            #     );
            # $2 = CommunicationLogObject
            # $3 = Kernel::System::CommunicationLog

            $Parser->{ObjectManager} = $1;
            $Parser->{ObjectName}    = $ObjectName // $2;
            $Parser->{Package}       = $3;

            return;
        }

        # fallback to pre ObjectManager syntax
        elsif ( $Paragraph =~ m{(my \s \$ ([^\s]+) \s+ = \s+ (Kernel::[^\-]+))}x && $Parser->{FunctionName} eq 'new') {

            # $1 = my $WebUserAgentObject = Kernel::System::WebUserAgent
            # $2 = WebUserAgentObject
            # $3 = Kernel::System::WebUserAgent

            $Parser->{ObjectManager} = $1;
            $Parser->{ObjectName}    = $ObjectName // $2;
            $Parser->{Package}       = $3;

            return;
        }

        return if !$Parser->{ObjectName};
        return if $Parser->{FunctionName} eq 'new';

        # special fix for $UnitTestObject->IsDeeply
        # to $Self->IsDeeply
        $Paragraph =~ s{\->\s+$Parser->{FunctionName}}{->$Parser->{FunctionName}}xms;

        my $CallObjectName = $Parser->{CallObjectMapping}->{ $Parser->{ObjectName} };
        $CallObjectName ||= $Parser->{ObjectName};

        # this normalizes the object of the function call
        # to match the one we are getting with our $Object snippet
        # because some Znuny framework objects have other Object names
        # in their POD function calls that in in the new POD
        # (e.g EmailObject Send = $SendObject->Send)
        $Paragraph =~ s{\$[^\s]+(\->$Parser->{FunctionName})}{\$$CallObjectName$1}xms;

        push @{$FunctionCallsRef}, $Paragraph;
    }
    elsif ( $FunctionCallsRef->[-1] && $Parser->{FunctionName} ne 'new' ) {
        $FunctionCallsRef->[-1] .= $Paragraph;
    }

    if ( $Paragraph !~ m{(\);|\})\n\n}xms ) {
        $Parser->{UnfinishedFunction} = 1;
    }
    else {

# FOR DEBUGGING PURPOSES
# if ( $FunctionCallsRef->[-1] && $Paragraph !~ m{\);\s+\z}xms ) {
#     use Data::Dumper;
#     print STDERR $Parser->{FunctionName} . ': Debug Dump - ZnunyPODParser - FunctionCall = ' . Dumper($FunctionCallsRef->[-1]) . "\n";
# }

        # if code block is present change
        # indentation to start right at
        # line beginning
        if ( $FunctionCallsRef->[-1] ) {

            $FunctionCallsRef->[-1] =~ s{\s+\z}{}xms;
            $FunctionCallsRef->[-1] =~ s{\A(\s+)}{}xms;

            my $Indentation = $1;
            $FunctionCallsRef->[-1] =~ s{^\Q$Indentation\E}{}xmsg;
        }

        $Parser->{UnfinishedFunction} = 0;

    }
}

sub textblock {    ## no critic
    # for debugging purposes:
    # my ($Parser, $Paragraph, $LineNum) = @_;
    # ## Translate/Format this block of text; sample actions might be:
    # my $OutFh = $Parser->output_handle();
    # my $Expansion = $Parser->interpolate($Paragraph, $LineNum);
    # print $OutFh "3: ". $Expansion ."\n";
}

sub interior_sequence {    ## no critic

}

1;